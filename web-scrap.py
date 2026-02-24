"""
LinkedIn Scraper - Final Fixed Version
Debug se pata chala: div.base-card = 60 elements ✓
CAPTCHA avoid karne ke liye visible mode + delays
"""

import json
import time
import random
import logging
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

LINKEDIN_DIR = Path("data/linkedin")
LINKEDIN_DIR.mkdir(parents=True, exist_ok=True)

LINKEDIN_JOBS = [
    "software engineer",
    "data scientist",
    "machine learning engineer",
    "python developer",
    "backend developer",
    "frontend developer",
    "devops engineer",
    "data analyst",
    "full stack developer",
    "AI engineer",
]

def random_delay(a=3, b=7):
    t = random.uniform(a, b)
    time.sleep(t)

def save_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log.info(f"✓ Saved: {filepath} ({len(data)} records)")

def get_driver():
    opts = Options()
    # HEADLESS OFF — CAPTCHA avoid karne ke liye
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=1920,1080")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=opts)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver

def parse_card(card):
    """div.base-card se data nikalo"""
    job = {}

    # Title
    for sel in ["h3.base-search-card__title", "h3", "h2"]:
        try:
            job["title"] = card.find_element(By.CSS_SELECTOR, sel).text.strip()
            if job["title"]: break
        except: continue
    job.setdefault("title", "")

    # Company
    for sel in ["h4.base-search-card__subtitle", "a.hidden-nested-link", "h4"]:
        try:
            job["company"] = card.find_element(By.CSS_SELECTOR, sel).text.strip()
            if job["company"]: break
        except: continue
    job.setdefault("company", "")

    # Location
    for sel in ["span.job-search-card__location", "span[class*='location']"]:
        try:
            job["location"] = card.find_element(By.CSS_SELECTOR, sel).text.strip()
            if job["location"]: break
        except: continue
    job.setdefault("location", "")

    # URL
    try:
        job["url"] = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link").get_attribute("href").split("?")[0]
    except:
        try:
            job["url"] = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href").split("?")[0]
        except:
            job["url"] = ""

    # Posted
    try:
        job["posted"] = card.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")
    except:
        job["posted"] = ""

    return job

def scrape_linkedin(max_per_keyword=100):
    log.info("=== LinkedIn Scraper Start (Fixed) ===")
    driver = get_driver()
    all_jobs = []

    try:
        for keyword in LINKEDIN_JOBS:
            log.info(f"\n{'='*50}")
            log.info(f"Keyword: '{keyword}'")
            keyword_jobs = []
            start = 0
            empty_pages = 0

            while len(keyword_jobs) < max_per_keyword and empty_pages < 3:
                url = (
                    f"https://www.linkedin.com/jobs/search?"
                    f"keywords={keyword.replace(' ', '%20')}"
                    f"&start={start}"
                )
                log.info(f"Page start={start} | Collected: {len(keyword_jobs)}")

                try:
                    driver.get(url)
                    random_delay(4, 8)

                    # Human-like scroll
                    for scroll_pct in [0.3, 0.6, 1.0]:
                        driver.execute_script(
                            f"window.scrollTo(0, document.body.scrollHeight * {scroll_pct});"
                        )
                        time.sleep(random.uniform(0.8, 1.5))

                    # Cards load hone ka wait
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.base-card"))
                        )
                    except:
                        log.warning("Cards load nahi hue, next page try karte hain")
                        empty_pages += 1
                        start += 25
                        random_delay(5, 10)
                        continue

                    # Cards fetch karo — debug se pata chala yeh kaam karta hai
                    cards = driver.find_elements(By.CSS_SELECTOR, "div.base-card")
                    log.info(f"Cards found: {len(cards)}")

                    if not cards:
                        empty_pages += 1
                        start += 25
                        continue

                    empty_pages = 0
                    page_jobs = 0

                    for card in cards:
                        try:
                            job = parse_card(card)
                            job["keyword"] = keyword
                            job["source"] = "linkedin"
                            job["scraped_at"] = datetime.now().isoformat()

                            if job["title"]:
                                keyword_jobs.append(job)
                                page_jobs += 1
                                log.info(f"  ✓ {job['title']} | {job['company']} | {job['location']}")

                        except Exception as e:
                            log.warning(f"Card parse error: {e}")
                            continue

                    log.info(f"Page jobs: {page_jobs} | Total: {len(keyword_jobs)}")
                    start += 25
                    random_delay(5, 10)

                except Exception as e:
                    log.error(f"Page error: {e}")
                    empty_pages += 1
                    start += 25
                    random_delay(5, 10)

            # Descriptions (top 10 per keyword — zyada karoge to ban ho sakta)
            log.info(f"Fetching descriptions for top 10 jobs...")
            for job in keyword_jobs[:10]:
                if not job.get("url"):
                    continue
                try:
                    driver.get(job["url"])
                    random_delay(3, 6)
                    for sel in ["div.show-more-less-html__markup", "div.description__text"]:
                        try:
                            el = driver.find_element(By.CSS_SELECTOR, sel)
                            job["description"] = el.text.strip()
                            break
                        except: continue
                    job.setdefault("description", "")
                except Exception as e:
                    log.warning(f"Desc error: {e}")

            all_jobs.extend(keyword_jobs)

            # Save per keyword
            fname = LINKEDIN_DIR / f"{keyword.replace(' ', '_')}.json"
            save_json(keyword_jobs, fname)

            # Keywords ke beech zyada wait (ban avoid)
            wait = random.uniform(15, 25)
            log.info(f"Waiting {wait:.0f}s before next keyword...")
            time.sleep(wait)

    finally:
        driver.quit()

    save_json(all_jobs, LINKEDIN_DIR / "all_linkedin_jobs.json")
    log.info(f"\n{'='*50}")
    log.info(f"LINKEDIN TOTAL: {len(all_jobs)} jobs saved")
    return all_jobs


if __name__ == "__main__":
    data = scrape_linkedin(max_per_keyword=100)
    print(f"\n✓ Done! Total: {len(data)} jobs")
    print(f"✓ Files saved in: data/linkedin/")