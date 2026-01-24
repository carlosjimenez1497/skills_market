from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from sqlalchemy.orm import Query as SAQuery
from .db import get_db
from .models import Job
import os

app = FastAPI(title="Job API")


origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# For local dev. Lock down later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
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
