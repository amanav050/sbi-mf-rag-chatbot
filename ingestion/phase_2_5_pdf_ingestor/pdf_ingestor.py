import requests
import os
import json
import re
import logging
import fitz  # PyMuPDF
import pdfplumber
from datetime import datetime

logger = logging.getLogger(__name__)

RAW_PDF_DIR = "ingestion/raw/pdf"
os.makedirs(RAW_PDF_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SBIMFResearchBot/1.0; +educational-project)"
}


def make_filename(scheme_name: str, doc_type: str) -> str:
    safe_name = re.sub(r"[^a-z0-9]", "_", scheme_name.lower())
    return f"{safe_name}_{doc_type}"


def download_pdf(url: str, dest_path: str) -> bool:
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=30)
        if response.status_code == 200:
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        logger.error(f"Download failed: status {response.status_code} for {url}")
        return False
    except Exception as e:
        logger.error(f"Download exception for {url}: {e}")
        return False


def extract_text_pymupdf(pdf_path: str) -> list[str]:
    pages = []
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        pages.append(text)
    doc.close()
    return pages


def extract_text_pdfplumber(pdf_path: str, page_num: int) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        if page_num < len(pdf.pages):
            return pdf.pages[page_num].extract_text() or ""
    return ""


def ingest_pdf(source: dict):
    url = source["url"]
    scheme_name = source["scheme_name"]
    doc_type = source["doc_type"]
    today = datetime.now().strftime("%Y-%m-%d")

    filename = make_filename(scheme_name, doc_type)
    pdf_path = os.path.join(RAW_PDF_DIR, f"{filename}.pdf")
    txt_path = os.path.join(RAW_PDF_DIR, f"{filename}.txt")
    meta_path = os.path.join(RAW_PDF_DIR, f"{filename}.json")

    logger.info(f"Downloading PDF: {url}")
    success = download_pdf(url, pdf_path)
    if not success:
        return

    pages_text = extract_text_pymupdf(pdf_path)
    full_text_parts = []

    for i, page_text in enumerate(pages_text):
        if not page_text.strip():
            logger.warning(f"Page {i+1} empty via PyMuPDF, trying pdfplumber fallback")
            page_text = extract_text_pdfplumber(pdf_path, i)
        full_text_parts.append(f"[PAGE {i+1}]\n{page_text}")

    full_text = "\n\n".join(full_text_parts)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    metadata = {
        "url": url,
        "scheme_name": scheme_name,
        "doc_type": doc_type,
        "source_type": "pdf",
        "ingestion_date": today,
        "page_count": len(pages_text),
        "char_count": len(full_text),
        "filename": filename
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Saved {filename}.txt ({len(pages_text)} pages, {len(full_text)} chars)")
