import requests
import time
import logging
import os
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SBIMFResearchBot/1.0; +educational-project)"
}
RAW_HTML_DIR = "ingestion/raw/html"
os.makedirs(RAW_HTML_DIR, exist_ok=True)


def fetch_with_retry(url: str, retries: int = 3) -> requests.Response | None:
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                return response
            logger.warning(f"Attempt {attempt+1}: status {response.status_code} for {url}")
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt+1} failed for {url}: {e}")
        time.sleep(2 ** attempt)
    return None


def clean_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned


def make_filename(scheme_name: str, doc_type: str, date_str: str) -> str:
    safe_name = re.sub(r"[^a-z0-9]", "_", scheme_name.lower())
    return f"{safe_name}_{doc_type}_{date_str}"


def scrape_url(source: dict):
    url = source["url"]
    scheme_name = source["scheme_name"]
    doc_type = source["doc_type"]
    today = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"Scraping: {url}")
    response = fetch_with_retry(url)

    if not response:
        logger.error(f"All retries failed for {url}")
        return

    text = clean_html(response.text)
    filename = make_filename(scheme_name, doc_type, today)

    txt_path = os.path.join(RAW_HTML_DIR, f"{filename}.txt")
    meta_path = os.path.join(RAW_HTML_DIR, f"{filename}.json")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    metadata = {
        "url": url,
        "scheme_name": scheme_name,
        "doc_type": doc_type,
        "source_type": "html",
        "scraped_date": today,
        "char_count": len(text),
        "filename": filename
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    time.sleep(2)
    logger.info(f"Saved {filename}.txt ({len(text)} chars)")
