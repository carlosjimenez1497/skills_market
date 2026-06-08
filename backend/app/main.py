from fastapi import FastAPI, Depends, Query, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from sqlalchemy.orm import Query as SAQuery
from .db import get_db
from .models import Job
import os
import json
import re

import requests as http_client
from bs4 import BeautifulSoup

try:
    import anthropic as _anthropic
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

app = FastAPI(title="Job API")


origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
origin_regex = os.getenv("CORS_ORIGIN_REGEX", "")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_origin_regex=origin_regex or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CountOut(BaseModel):
    total: int


class JobOut(BaseModel):
    id: int
    job_id: str | None
    job_view_url: str | None
    company: str | None
    title: str | None
    location: str | None
    description: str | None
    language_code: str | None
    first_seen: datetime | None
    last_seen: datetime | None
    times_seen: int

    model_config = {"from_attributes": True}

class JobUpsertIn(BaseModel):
    # Identity & dedup
    job_id: str | None = None
    fingerprint: str

    # Source
    source: str
    source_url: str
    job_view_url: str | None = None

    # Job content
    company: str | None = None
    title: str | None = None
    location: str | None = None
    description: str | None = None

    # Metadata
    language_code: str | None = None

def apply_job_filters(
    q: SAQuery,
    *,
    track: str | None,
    language: str | None,
    keywords: str | None,
):
    # Track filter only if you actually have Job.track
    # if track:
    #     q = q.filter(Job.track == track)

    if language:
        q = q.filter(Job.language_code == language)

    if keywords:
        parts = [p.strip() for p in keywords.split(",") if p.strip()]
        for kw in parts:
            like = f"%{kw}%"
            q = q.filter(
                or_(
                    Job.title.ilike(like),
                    Job.description.ilike(like),
                )
            )

    return q


# --- optional simple auth for your local scraper ---
def require_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("SCRAPER_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/api/jobs", response_model=list[JobOut])
def list_jobs(
    db: Session = Depends(get_db),
    track: str | None = Query(default=None, description="software|finance"),
    language: str | None = Query(default=None, description="e.g. en, it"),
    keywords: str | None = Query(default=None, description="Comma-separated keywords; all must match"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    q = db.query(Job)
    q = apply_job_filters(q, track=track, language=language, keywords=keywords)
    q = q.order_by(Job.id.desc()).offset(offset).limit(limit)
    return q.all()

@app.get("/api/jobs/count", response_model=CountOut)
def count_jobs(
    db: Session = Depends(get_db),
    track: str | None = Query(default=None, description="software|finance"),
    language: str | None = Query(default=None, description="e.g. en, it"),
    keywords: str | None = Query(default=None, description="Comma-separated keywords; all must match"),
):
    q = db.query(Job)
    q = apply_job_filters(q, track=track, language=language, keywords=keywords)
    total = q.count()
    return {"total": total}

class FetchUrlIn(BaseModel):
    url: str

class FetchUrlOut(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    description: str | None = None
    job_url: str
    method: str  # jsonld | opengraph | heuristic | llm | partial | failed

def _count_filled(d: dict, keys: tuple) -> int:
    return sum(1 for k in keys if d.get(k))

@app.post("/api/jobs/fetch-url", response_model=FetchUrlOut)
def fetch_url_meta(payload: FetchUrlIn):
    url = payload.url
    result: dict = {"job_url": url, "method": "failed"}

    try:
        resp = http_client.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; JobFetcher/1.0)"},
            timeout=15,
            allow_redirects=True,
        )
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not fetch URL: {e}")

    soup = BeautifulSoup(html, "html.parser")

    # --- Layer 1: JSON-LD (schema.org/JobPosting) ---
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
            if isinstance(data, list):
                data = next(
                    (d for d in data if isinstance(d, dict) and d.get("@type") == "JobPosting"),
                    None,
                )
            if isinstance(data, dict) and data.get("@type") == "JobPosting":
                result["title"] = data.get("title")
                org = data.get("hiringOrganization")
                if isinstance(org, dict):
                    result["company"] = org.get("name")
                elif isinstance(org, str):
                    result["company"] = org
                loc = data.get("jobLocation")
                if isinstance(loc, list) and loc:
                    loc = loc[0]
                if isinstance(loc, dict):
                    addr = loc.get("address") or {}
                    result["location"] = (
                        addr.get("addressLocality")
                        or addr.get("addressRegion")
                        or addr.get("addressCountry")
                    )
                raw_desc = data.get("description", "")
                if raw_desc:
                    result["description"] = BeautifulSoup(raw_desc, "html.parser").get_text(
                        separator="\n", strip=True
                    )[:3000]
                result["method"] = "jsonld"
                break
        except Exception:
            continue

    # --- Layer 2: OpenGraph / meta tags ---
    if _count_filled(result, ("title", "company", "location")) < 2:
        def og(prop):
            return soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        og_title = og("og:title") or og("title")
        og_desc = og("og:description") or og("description")
        if og_title and not result.get("title"):
            result["title"] = (og_title.get("content") or "").strip() or None
        if og_desc and not result.get("description"):
            result["description"] = (og_desc.get("content") or "").strip() or None
        if result.get("title") or result.get("description"):
            result.setdefault("method", "opengraph")
            if result["method"] == "failed":
                result["method"] = "opengraph"

    # --- Layer 3: Heuristic selectors ---
    if _count_filled(result, ("title", "company", "location")) < 2:
        if not result.get("title"):
            h1 = soup.find("h1")
            if h1:
                result["title"] = h1.get_text(strip=True) or None
        if result.get("title") and result["method"] == "failed":
            result["method"] = "heuristic"

    # --- Layer 4: LLM fallback via Claude Haiku ---
    if _count_filled(result, ("title", "company", "location")) < 2 and _HAS_ANTHROPIC:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            try:
                for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    tag.decompose()
                clean_text = soup.get_text(separator="\n", strip=True)[:4000]

                client = _anthropic.Anthropic(api_key=api_key)
                msg = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=300,
                    messages=[{
                        "role": "user",
                        "content": (
                            "Extract job posting info from the text below. "
                            "Return ONLY a JSON object with these fields (null if not found):\n"
                            '{"title": "...", "company": "...", "location": "...", '
                            '"description": "first 300 chars of the actual job description"}\n\n'
                            f"Text:\n{clean_text}"
                        ),
                    }],
                )
                raw = msg.content[0].text.strip()
                m = re.search(r"\{.*\}", raw, re.DOTALL)
                if m:
                    parsed = json.loads(m.group())
                    for k in ("title", "company", "location", "description"):
                        if not result.get(k) and parsed.get(k):
                            result[k] = parsed[k]
                    result["method"] = "llm"
            except Exception:
                pass

    if result["method"] == "failed" and _count_filled(result, ("title", "company", "description")) > 0:
        result["method"] = "partial"

    return result


@app.post("/api/jobs/upsert")
def upsert_job(
    payload: JobUpsertIn,
    db: Session = Depends(get_db),
    # _=Depends(require_api_key),  # remove if you don't want auth yet
):
    now = datetime.utcnow()

    existing = db.query(Job).filter(Job.fingerprint == payload.fingerprint).first()

    if existing:
        # update existing record
        existing.last_seen = now
        existing.times_seen = (existing.times_seen or 0) + 1
        existing.updated_at = now

        # refresh fields when new values exist
        for k, v in payload.model_dump().items():
            if v is not None and v != "":
                setattr(existing, k, v)

        db.commit()
        return {"status": "updated", "id": existing.id}

    # insert new record
    j = Job(**payload.model_dump())
    j.first_seen = now
    j.last_seen = now
    j.created_at = now
    j.updated_at = now
    j.times_seen = 1

    db.add(j)
    db.commit()
    db.refresh(j)
    return {"status": "inserted", "id": j.id}
