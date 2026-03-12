from playwright.sync_api import sync_playwright

USER_DATA_DIR = "pw_profile_linkedin"  # folder that will store cookies/session

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,
    )
    page = context.new_page()
    page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")

    print("Log in manually in the opened browser window.")
    print("When you're done, go to https://www.linkedin.com/jobs/ and wait until it loads.")

    # Wait until we are no longer on login/checkpoint pages
    page.wait_for_url(lambda url: ("login" not in url and "checkpoint" not in url), timeout=180_000)

    # Optional: ensure some LinkedIn UI is present
    page.wait_for_timeout(2000)

    print("Session saved in folder:", USER_DATA_DIR)
    context.close()
