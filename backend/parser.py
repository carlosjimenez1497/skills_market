import sqlite3
from pathlib import Path
from playwright.sync_api import sync_playwright
import hashlib
import re
# import time
# import datetime
import requests
import os

from utils.utils import write_log
from lang_detect import FastTextLangDetector

API_BASE = os.environ["API_BASE"]  # e.g. https://your-backend.onrender.com
DB_PATH = Path("db/jobs.db")
# JOB_URL = "https://www.linkedin.com/jobs/collections/top-applicant/"
# JOB_URL = "https://www.linkedin.com/jobs/search/?distance=25.0&f_E=2%2C3&f_TPR=r604800&geoId=102890719&keywords=Python%20Engineer&origin=JOBS_HOME_KEYWORD_HISTORY"
JOB_URL = "https://www.linkedin.com/jobs/search/?distance=25.0&f_E=2%2C3&f_TPR=r604800&geoId=102890719&keywords=software%20engineer&origin=JOB_SEARCH_PAGE_KEYWORD_AUTOCOMPLETE&refresh=true"
JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=3%2C4&f_TPR=r86400&keywords=finance%20business%20partner&origin=JOB_SEARCH_PAGE_JOB_FILTER"
MAX_JOBS_PER_PAGE = 25
MAX_PAGES = 25



detector = FastTextLangDetector("lang_models/lid.176.ftz")

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

def get_scroll_container(page):
    # This is the scrollable viewport in your DOM
    content_div = page.locator(
        "div.scaffold-layout__list > header + div"
    ).first
    if content_div.count() == 0:
        raise RuntimeError("Could not find scroll container: div.scaffold-layout__list")
    return content_div

def get_results_number(page):
    subtitle = page.locator("div.jobs-search-results-list__title-heading div").first
    results_text = subtitle.inner_text().strip()
    if "results" in results_text:
        if "\n" in results_text:
            results_text = results_text.split("\n")[-1]
            results_text = results_text.split(" ")[0]
            if "," in results_text:
                results_text = results_text.split(",")[0] + results_text.split(",")[1]
            results_text = int(results_text)
            print("Results:", results_text)
            write_log(f"Results: {results_text}")
            return results_text
        else:
            results_text = results_text.split(" ")[0]
            if "," in results_text:
                results_text = results_text.split(",")[0] + results_text.split(",")[1]
            results_text = int(results_text)
            print("Results:", results_text)
            write_log(f"Results: {results_text}")
            return results_text
    else:
        print("Results: who knows")
        write_log("Results: who knows")
        return None
    

def scroll_container_by(page, container, amount: int):
    # scrollTop += amount

    page.evaluate(
        """(params) => {
            params.el.scrollTop = params.el.scrollTop + params.dy;
        }""",
        {
            "el": container.element_handle(),
            "dy": amount
        }
    )


def click_card_index_with_scroll(page, container, i: int, max_tries: int = 5):
    """
    Ensures card i is interactable by scrolling the container progressively.
    Returns job_id string.
    """
    for attempt in range(max_tries):
        # Re-query fresh each attempt (DOM can change)
        card = page.locator("li[data-occludable-job-id]").nth(i)
        job_id = card.get_attribute("data-occludable-job-id") or ""

        link = card.locator("a.job-card-container__link").first

        try:
            # Quick check: if link is visible, try click
            if link.count() > 0 and link.is_visible():
                link.click(timeout=3000)
                return job_id

            # If not visible, scroll down a bit and retry
            scroll_container_by(page, container, 500)
            page.wait_for_timeout(250)

        except Exception as e:
            # If click failed (overlay, etc.), scroll a bit and retry
            scroll_container_by(page, container, 350)
            page.wait_for_timeout(300)
            print(f"Error while scrolling {e}")
            write_log(f"Error while scrolling {e}")

    write_log(f"Could not click card index {i} after {max_tries} tries")
    raise RuntimeError(f"Could not click card index {i} after {max_tries} tries")


def process_current_page(page, container):
    cards = page.locator("li[data-occludable-job-id]")
    count = min(cards.count(), MAX_JOBS_PER_PAGE)
    print("Found cards:", cards.count(), "-> will process:", count)
    write_log(f"Found cards: {cards.count()}-> will process: {count}")

    for i in range(count):
        job_id = click_card_index_with_scroll(page, container, i)

        # Wait for right panel to update to this job
        page.wait_for_selector("div.job-details-jobs-unified-top-card__job-title", timeout=15_000)
        # page.wait_for_function(
        #     """(jobId) => {
        #         const a = document.querySelector('div.job-details-jobs-unified-top-card__job-title h1 a');
        #         return a && a.getAttribute('href') && a.getAttribute('href').includes('/jobs/view/' + jobId);
        #     }""",
        #     job_id,
        #     timeout=15_000
        # )

        # ---- extract fields ----
        # --- Job title ---
        title_loc = page.locator(
            "div.job-details-jobs-unified-top-card__job-title h1 a"
        ).first
        if title_loc.count() == 0:
            title_loc = page.locator(
                "div.job-details-jobs-unified-top-card__job-title h1"
            ).first
        title = title_loc.inner_text().strip()
        job_href = title_loc.get_attribute("href") or ""
        job_view_url = normalize_job_link(job_href)

        # --- Company name ---
        company = page.locator(
            "div.job-details-jobs-unified-top-card__company-name a"
        ).first.inner_text().strip()

        # --- Location (first low-emphasis span) ---
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
            # Fallback: save the whole visible text (not ideal, but proves extraction works)
            description = page.locator("body").inner_text().strip()

        r1, r2 = detector.detect_top2(description)
        fingerprint = make_fingerprint(company, title, location)
        # now = datetime.datetime.utcnow().isoformat()

        # ---- save to SQLite ----
        payload = {
            "source": "linkedin",
            "source_url": JOB_URL,
            "job_view_url": job_view_url,
            "job_id": job_id,
            "company": company or None,
            "title": title or None,
            "location": location or None,
            "description": description or None,
            "language_code": r1.code,  # set if you have it
            "fingerprint": fingerprint,
        }

        try:
            result = upsert_job_via_api(payload)
            print(f"[{i+1}/{count}] {result['status']}: {company} — {title} — {location}")
            write_log(f"[{i+1}/{count}] {result['status']}: {company} — {title} — {location}")
        except Exception as e:
            print(f"[{i+1}/{count}] API upsert failed: {e}")
            write_log(f"[{i+1}/{count}] API upsert failed: {e}")


        # print(f"[{i+1}/{count}] Saved: {company} — {title} — {location}")
        # write_log(f"[{i+1}/{count}] Saved: {company} — {title} — {location}")
        # print("Saved job to SQLite ✔")
        page.wait_for_timeout(800)

def get_first_job_id(page) -> str:
    page.wait_for_selector("li[data-occludable-job-id]", timeout=15_000)
    return page.locator("li[data-occludable-job-id]").first.get_attribute("data-occludable-job-id") or ""

def upsert_job_via_api(job_payload: dict):
    url = f"{API_BASE}/api/jobs/upsert"
    # headers = {}
    # if SCRAPER_API_KEY:
    #     headers["X-API-Key"] = SCRAPER_API_KEY

    # r = requests.post(url, json=job_payload, headers=headers, timeout=30)
    r = requests.post(url, json=job_payload, timeout=30)
    r.raise_for_status()
    return r.json()


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

    
    
    page.wait_for_selector("li[data-occludable-job-id]", timeout=15_000)
    container = get_scroll_container(page)

    total_results = get_results_number(page)
    if (total_results % 25) == 0:
        number_of_pages = int(total_results // 25)
    else:
        number_of_pages = int((total_results // 25) + 1)
    # Give time for the job details panel to render
    # Wait for the left list to be present
    
    

    for page_idx in range(MAX_PAGES):
        print(f"\n=== Processing page {page_idx+1} ===")
        write_log(f"\n=== Processing page {page_idx+1} ===")

        # process the current page’s 25 cards (your existing logic)
        process_current_page(page, container)

        # Find "Next" button
        next_btn = page.locator(
            'button[aria-label="View next page"], button[aria-label*="Next"], button.artdeco-pagination__button--next'
        ).first

        # Stop condition
        if next_btn.count() == 0:
            print("No Next button found. Done.")
            write_log("No Next button found. Done.")
            break

        aria_disabled = next_btn.get_attribute("aria-disabled")
        if (aria_disabled == "true") or next_btn.is_disabled():
            print("Next button disabled. Done.")
            write_log("Next button disabled. Done.")
            break

        # Capture current first job id to detect page change
        before = get_first_job_id(page)

        # Click next
        next_btn.click()

        # Wait for job list to refresh (first job id changes)
        page.wait_for_function(
            """(prevId) => {
                const li = document.querySelector('li[data-occludable-job-id]');
                const id = li?.getAttribute('data-occludable-job-id') || '';
                return id && id !== prevId;
            }""",
            arg=before
        )

        # Optional small pause
        page.wait_for_timeout(800)
    else:
        print("Hit MAX_PAGES safety cap.")
        write_log("Hit MAX_PAGES safety cap.")
    context.close()
