# import sqlite3
from pathlib import Path
import time
from playwright.sync_api import sync_playwright
import hashlib
import re
# import time
# import datetime
import requests
import os
from dotenv import load_dotenv
from utils.utils import write_log
from lang_detect import FastTextLangDetector
import psutil, os

# System memory
mem = psutil.virtual_memory()

# Python process memory
process = psutil.Process(os.getpid())

load_dotenv()

API_BASE = os.environ["API_BASE"]  # e.g. https://your-backend.onrender.com
DB_PATH = Path("db/jobs.db")
### Top Applcant
# JOB_URL = "https://www.linkedin.com/jobs/collections/top-applicant/"
### Python Engineer in Netherlands, past week, entry associereate level
# JOB_URL = "https://www.linkedin.com/jobs/search/?distance=25.0&f_E=2%2C3&f_TPR=r86400&geoId=102890719&keywords=Python%20Engineer&origin=JOBS_HOME_KEYWORD_HISTORY"
### Software Engineer in Netherlands, past week, entry associate level
# JOB_URL = "https://www.linkedin.com/jobs/search/?distance=25.0&f_E=2%2C3&f_TPR=r86400&geoId=102890719&keywords=software%20engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
### Sofware engineer python in Netherlands, past week, entry associate level
# JOB_URL = "https://www.linkedin.com/jobs/search/?distance=25&f_E=2%2C3&f_TPR=r86400&f_WT=3%2C1%2C2&geoId=102890719&keywords=Software%20Engineer%20python&origin=JOB_SEARCH_PAGE_JOB_FILTER"
### Finance business partner in Netherlands, past day, all experience levels
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=3%2C4&f_TPR=r86400&keywords=finance%20business%20partner&origin=JOB_SEARCH_PAGE_JOB_FILTER"
#### Python AND (software OR%20backend OR engineer OR simulation)%20AND%20Netherlands
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=1%2C2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Python%20AND%20(software%20OR%20backend%20OR%20engineer%20OR%20simulation)%20AND%20Netherlands&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&spellCorrectionEnabled=true"
#### Somilation software engineer in Netherlands, past day, entry associate level
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Simulation%20Software%20Engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&spellCorrectionEnabled=true"
#### Engineering software engineer in Netherlands, past day, entry associate level
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Engineering%20Software%20Developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Research%20Software%20Developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Scientific%20Software%20Developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Application%20Engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&trk=d_flagship3_salary_explorer"
# JOB_URL = "https://www.linkedin.com/jobs/search/?distance=25&f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Netherlands%20AND%20Python%20AND%20automotive%20AND%20simulation&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=civil%20engineer%20AND%20python&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=civil%20engineer%20python&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=civil%20engineer&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=traffic%20engineer&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r604800&geoId=102890719&keywords=traffic%20engineer%20python&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r604800&geoId=102890719&keywords=transport%20engineer%20python&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r604800&geoId=102890719&keywords=transport%20modeller%20python&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=transport%20modeller&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r604800&geoId=102890719&keywords=automotive%20engineer&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=automotive%20simulation&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=automotive%20simulation%20python&origin=JOBS_HOME_KEYWORD_HISTORY"
MAX_JOBS_PER_PAGE = 25
MAX_PAGES = 30



detector = FastTextLangDetector("lang_models/lid.176.ftz")

# ---------- helpers ----------
def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def make_fingerprint(company: str, title: str, location: str) -> str:
    base = f"{normalize(company)}|{normalize(title)}|{normalize(location)}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()


def add_start_param(url: str, start: int) -> str:
    if 'start=' in url:
        url = re.sub(r'start=\d+', f'start={start}', url)
    else:
        if '?' in url:
            url += f'&start={start}'
        else:
            url += f'?start={start}'
    return url


# ---------- DB setup ----------
# def init_db():
#     with sqlite3.connect(DB_PATH) as conn:
#         conn.execute("""
#         CREATE TABLE IF NOT EXISTS jobs (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             source TEXT NOT NULL,
#             source_url TEXT NOT NULL,
#             company TEXT,
#             title TEXT,
#             location TEXT,
#             description TEXT,
#             fingerprint TEXT UNIQUE,
#             first_seen DATE,
#             last_seen DATE,
#             times_seen INTEGER DEFAULT 1,
#             created_at TIMESTAMP,
#             updated_at TIMESTAMP
#         )
#         """)
#         conn.commit()

def normalize_job_link(job_href):
    job_view_url = None
    m = re.search(r"/jobs/view/(\d+)", job_href)
    if m:
        job_id = m.group(1)
        job_view_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
    return job_view_url


# ---------- main ----------
# init_db()

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


def process_current_page(page, container, JOB_URL):
    cards = page.locator("li[data-occludable-job-id]")
    count = min(cards.count(), MAX_JOBS_PER_PAGE)
    print("Found cards:", cards.count(), "-> will process:", count)
    write_log(f"Found cards: {cards.count()}-> will process: {count}")

    for i in range(count):
        try:
            job_id = click_card_index_with_scroll(page, container, i)
            # System memory
            mem = psutil.virtual_memory()

            # Python process memory
            process = psutil.Process(os.getpid())
            # print("=== SYSTEM ===")
            print(f"Used: {mem.percent}% | Available: {mem.available / (1024**3):.2f} GB")
            write_log(f"Used: {mem.percent}% | Available: {mem.available / (1024**3):.2f} GB")

            # print("=== PYTHON ===")
            print(f"RSS: {process.memory_info().rss / (1024**2):.2f} MB")
            write_log(f"RSS: {process.memory_info().rss / (1024**2):.2f} MB")
        except Exception as e:
            print(f"Error occurred while processing card {i}: {e}")
            write_log(f"Error occurred while processing card {i}: {e}")
            time.sleep(0.5)
            continue

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
        company_loc = page.locator(
            "div.job-details-jobs-unified-top-card__company-name a"
        ).first
        if company_loc.count() == 0:
            company_loc = page.locator(
                "div.job-details-jobs-unified-top-card__company-name"
            ).first
        company = company_loc.inner_text().strip()

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

        time.sleep(0.5)  # small delay to avoid overwhelming the API or hitting rate limits

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

def run(JOB_URL):
    batch_size = 4

    # First, get total_results
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="pw_profile_linkedin",
            headless=True,
        )
        page = context.new_page()

        page.goto(JOB_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # manual login if needed
        if "login" in page.url or "checkpoint" in page.url:
            print("Please log in manually in the opened browser window...")
            # Wait up to 2 minutes for you to finish logging in
            page.wait_for_url("**/jobs/**", timeout=120_000)

        page.wait_for_selector("li[data-occludable-job-id]", timeout=65_000)

        total_results = get_results_number(page)
        if total_results is None:
            print("Could not get results number")
            write_log("Could not get results number")
            context.close()
            return

        if (total_results % 25) == 0:
            number_of_pages = int(total_results // 25)
        else:
            number_of_pages = int((total_results // 25) + 1)

        context.close()

    # Now, batch processing
    for batch_start in range(0, number_of_pages, batch_size):
        start_param = batch_start * 25
        current_url = add_start_param(JOB_URL, start_param)

        with sync_playwright() as p:
            print(f"Starting batch from page {batch_start + 1} with URL: {current_url}")
            write_log(f"Starting batch from page {batch_start + 1} with URL: {current_url}")

            context = p.chromium.launch_persistent_context(
                user_data_dir="pw_profile_linkedin",
                headless=True,
            )
            page = context.new_page()

            page.goto(current_url, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            # Assuming login is remembered
            page.wait_for_selector("li[data-occludable-job-id]", timeout=65_000)
            container = get_scroll_container(page)

            pages_in_batch = min(batch_size, number_of_pages - batch_start)

            for page_in_batch in range(pages_in_batch):
                print(f"\n=== Processing page {batch_start + page_in_batch + 1} ===")
                write_log(f"\n=== Processing page {batch_start + page_in_batch + 1} ===")

                process_current_page(page, container, current_url)

                if page_in_batch < pages_in_batch - 1:
                    # Click next
                    next_btn = page.locator(
                        'button[aria-label="View next page"], button[aria-label*="Next"], button.artdeco-pagination__button--next'
                    ).first

                    if next_btn.count() == 0:
                        print("No Next button found. Stopping batch.")
                        write_log("No Next button found. Stopping batch.")
                        break

                    aria_disabled = next_btn.get_attribute("aria-disabled")
                    if (aria_disabled == "true") or next_btn.is_disabled():
                        print("Next button disabled. Stopping batch.")
                        write_log("Next button disabled. Stopping batch.")
                        break

                    before = get_first_job_id(page)

                    next_btn.click()

                    page.wait_for_function(
                        """(prevId) => {
                            const li = document.querySelector('li[data-occludable-job-id]');
                            const id = li?.getAttribute('data-occludable-job-id') || '';
                            return id && id !== prevId;
                        }""",
                        arg=before
                    )

                    page.wait_for_timeout(800)

            context.close()

if __name__ == "__main__":
    run()