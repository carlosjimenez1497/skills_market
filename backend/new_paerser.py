import sqlite3
from pathlib import Path
from playwright.sync_api import sync_playwright
import hashlib
import re
import time
import datetime

DB_PATH = Path("db/jobs.db")
JOB_URL = "https://www.linkedin.com/jobs/collections/top-applicant/"


# ---------- helpers ----------
def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def make_fingerprint(company: str, title: str, location: str) -> str:
    base = f"{normalize(company)}|{normalize(title)}|{normalize(location)}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()


# ---------- DB setup ----------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_url TEXT NOT NULL,
            company TEXT,
            title TEXT,
            location TEXT,
            description TEXT,
            fingerprint TEXT UNIQUE,
            first_seen DATE,
            last_seen DATE,
            times_seen INTEGER DEFAULT 1,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """)
        conn.commit()

def normalize_job_link(job_href):
    job_view_url = None
    m = re.search(r"/jobs/view/(\d+)", job_href)
    if m:
        job_id = m.group(1)
        job_view_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
    return job_view_url


# ---------- main ----------
init_db()

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir="pw_profile_linkedin",
        headless=False,
    )
    page = context.new_page()

    page.goto(JOB_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # manual login if needed
    if "login" in page.url or "checkpoint" in page.url:
        print("Please log in manually in the opened browser window...")
        # Wait up to 2 minutes for you to finish logging in
        page.wait_for_url("**/jobs/**", timeout=120_000)

    # Give time for the job details panel to render
    # Wait for the left list to be present
    page.wait_for_selector("li[data-occludable-job-id]", timeout=15_000)

    cards = page.locator("li[data-occludable-job-id]")
    count = min(cards.count(), MAX_JOBS_PER_PAGE)
    print("Found cards:", cards.count(), "-> will process:", count)

    for i in range(count):
        card = cards.nth(i)

        job_id = card.get_attribute("data-occludable-job-id") or ""
        link = card.locator("a.job-card-container__link").first

        # Make sure it's in view (helps reliability)
        link.scroll_into_view_if_needed()
        page.wait_for_timeout(300)

        # Click job card
        link.click()

        # Wait until the right panel updates to this job
        # We confirm by checking the top-card title link contains /jobs/view/<job_id>
        page.wait_for_selector("div.job-details-jobs-unified-top-card__job-title h1 a", timeout=15_000)
        page.wait_for_function(
            """(jobId) => {
                const a = document.querySelector('div.job-details-jobs-unified-top-card__job-title h1 a');
                return a && a.getAttribute('href') && a.getAttribute('href').includes('/jobs/view/' + jobId);
            }""",
            job_id,
            timeout=15_000
        )

        # ---- extract fields (your existing code) ----
        title_loc = page.locator(
            "div.job-details-jobs-unified-top-card__job-title h1 a"
        ).first
        title = title_loc.inner_text().strip()
        job_href = title_loc.get_attribute("href") or ""
        job_view_url = normalize_job_link(job_href)

        company = page.locator(
            "div.job-details-jobs-unified-top-card__company-name a"
        ).first.inner_text().strip()

        loc_loc = page.locator(
            "div.job-details-jobs-unified-top-card__primary-description-container "
            "span.tvm__text.tvm__text--low-emphasis"
        ).first
        location = loc_loc.inner_text().strip() if loc_loc.count() else ""

        desc_candidates = [
            "div.jobs-description-content__text",
            "div#job-details",
            "section[data-test-job-details-section]",
            "div.jobs-box__html-content",
        ]

        description = None
        for sel in desc_candidates:
            loc = page.locator(sel).first
            if loc.count() > 0:
                text = loc.inner_text().strip()
                if len(text) > 200:
                    description = text
                    break

        if not description:
            description = page.locator("body").inner_text().strip()

        fingerprint = make_fingerprint(company, title, location)
        now = datetime.datetime.utcnow().isoformat()

        # ---- save to SQLite ----
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()

            cur.execute("""
            INSERT OR IGNORE INTO jobs (
                source, source_url, job_view_url,
                company, title, location,
                description, fingerprint,
                first_seen, last_seen, times_seen,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATE('now'), DATE('now'), 1, ?, ?)
            """, (
                "linkedin",
                page.url,          # will include currentJobId as you click (good enough as "context url")
                job_view_url,      # stable /jobs/view/<id>/
                company,
                title,
                location,
                description,
                fingerprint,
                now,
                now
            ))

            if cur.rowcount == 0:
                cur.execute("""
                UPDATE jobs
                SET last_seen = DATE('now'),
                    times_seen = times_seen + 1,
                    updated_at = ?,
                    job_view_url = ?,
                    description = ?
                WHERE fingerprint = ?
                """, (now, job_view_url, description, fingerprint))

            conn.commit()

        print(f"[{i+1}/{count}] Saved: {company} — {title} — {location}")

        # Small pause so the UI isn’t hammered
        page.wait_for_timeout(800)
