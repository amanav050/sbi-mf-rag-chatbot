---
## INSTRUCTIONS FOR AI CODING ASSISTANT

This document is the **SINGLE SOURCE OF TRUTH** for the SBI MF RAG Chatbot project.

### How to use this document:
1. **READ the full phase section** before writing any code for that phase.
2. **USE the code provided EXACTLY as written.** Do not modify function names, variable names, folder paths, import statements, or logic unless the user explicitly asks.
3. **DO NOT install packages** not listed in `requirements.txt`.
4. **DO NOT create files or folders** not specified in this document.
5. **COMPLETE one phase at a time.** Never jump ahead to future phases.
6. **AFTER each phase, confirm:**
   - Which files were created
   - That they match this document exactly
   - Any errors or deviations encountered
7. **If anything is ambiguous, ASK — do not assume.**
8. **PHASE DEPENDENCY CHAIN:** Phase 0 → 1 → 1.5 → 2 → 2.5 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11. Never skip.

---

# SBI MF RAG Chatbot — Full System Architecture

> Single source of truth for building the SBI Mutual Fund FAQ RAG Chatbot.

---

## PROJECT OVERVIEW

- **Goal:** A production-ready, facts-only RAG chatbot that answers queries about SBI Mutual Fund schemes using only official public sources. No investment advice. No opinions. Only verifiable, cited facts.
- **AMC:** SBI Mutual Fund (sbimf.com)
- **Schemes covered:**
  - SBI Large Cap Fund
  - SBI Flexicap Fund
  - SBI ELSS Tax Saver Fund
  - SBI Small Cap Fund

---

## TECH STACK (mandatory — no substitutions)

| Component | Tool | Why |
|---|---|---|
| HTML Scraping | requests + BeautifulSoup4 | Standard, lightweight |
| PDF Ingestion | PyMuPDF (primary), pdfplumber (fallback) | Best text extraction |
| Chunking | LangChain RecursiveCharacterTextSplitter | Overlapping chunks |
| Embedding | sentence-transformers bge-small-en-v1.5 (local, free) | No API cost |
| Vector DB | Chroma Cloud (trychroma.com) | Managed, free tier |
| Scheduler | GitHub Actions CRON | Free CI/CD |
| LLM | Groq API — llama-3.1-8b-instant | Fast, free tier |
| API | FastAPI + uvicorn | Async, auto-docs |
| UI | Plain HTML + CSS + JS (no frameworks) | Lightweight |

---

## FOLDER STRUCTURE (create exactly this — no additions, no renames)

```
sbi-mf-rag-chatbot/
├── docs/
│   └── rag-architecture.md          ← THIS file
├── corpus/
│   └── corpus.json                  ← master list of all URLs and PDFs
├── ingestion/
│   ├── router.py                    ← source classification router
│   ├── raw/
│   │   ├── html/                    ← scraped HTML content saved as .txt
│   │   └── pdf/                     ← downloaded PDFs
│   ├── chunks/                      ← chunked text saved as .json
│   ├── embeddings/                  ← embeddings saved as .json
│   ├── phase_2_scraper/
│   │   ├── scraper.py
│   │   └── utils.py
│   ├── phase_2_5_pdf_ingestor/
│   │   ├── pdf_ingestor.py
│   │   └── utils.py
│   ├── phase_3_chunker/
│   │   └── chunker.py
│   ├── phase_4_embedder/
│   │   └── embedder.py
│   └── phase_5_vector_db/
│       └── vector_db.py
├── scheduler/
│   └── .github/
│       └── workflows/
│           ├── daily_ingest.yml     ← HTML pipeline, runs daily 9:15 AM IST
│           └── manual_pdf.yml       ← PDF pipeline, manual trigger only
├── query/
│   ├── phase_7_retriever/
│   │   └── retriever.py
│   ├── phase_8_llm/
│   │   └── llm_handler.py
│   └── phase_9_refusal/
│       ├── refusal_handler.py
│       └── citation_formatter.py
├── api/
│   └── phase_10_fastapi/
│       ├── main.py
│       ├── models.py
│       └── middleware.py
├── ui/
│   └── phase_11_ui/
│       ├── index.html
│       ├── style.css
│       └── app.js
├── .env                             ← gitignored, contains all API keys
├── .gitignore
└── requirements.txt
```

---

## ENVIRONMENT VARIABLES

**File:** `.env` at project root

```
CHROMA_API_KEY=your_chroma_api_key_here
CHROMA_TENANT=f0d857c0-c00b-4742-bf30-d9a10400d176
CHROMA_DATABASE=sbi_mf_rag
GROQ_API_KEY=your_groq_api_key_here
```

**File:** `.gitignore` at project root

```
.env
ingestion/raw/
ingestion/chunks/
ingestion/embeddings/
__pycache__/
*.pyc
.DS_Store
```

---

## REQUIREMENTS.TXT (exact versions — do not change)

```
requests==2.31.0
beautifulsoup4==4.12.3
pymupdf==1.24.1
pdfplumber==0.11.0
langchain==0.1.20
langchain-text-splitters==0.0.1
sentence-transformers==2.7.0
chromadb==0.5.0
fastapi==0.111.0
uvicorn==0.30.1
groq==0.9.0
python-dotenv==1.0.1
slowapi==0.1.9
```

---

## PHASE 0 — PROJECT SETUP

**Purpose:** Create the entire folder structure, environment, and configuration before any code is written.

**Steps:**
1. Create the folder structure exactly as shown above using `mkdir -p` for all nested directories.
2. Create `requirements.txt` with the exact contents above.
3. Create `.env` with placeholder values.
4. Create `.gitignore` with the entries above.
5. Run `pip install -r requirements.txt` to install all dependencies.
6. Verify installation by running:
   ```
   python -c "import chromadb; import groq; import fastapi; print('All dependencies installed')"
   ```

**Completion checklist:**
- [ ] All folders exist
- [ ] requirements.txt has all 13 packages with exact pinned versions
- [ ] .env has 4 placeholder keys
- [ ] .gitignore has all exclusion entries
- [ ] Verification import prints "All dependencies installed"

---

## PHASE 1 — CORPUS DEFINITION

**Purpose:** Create the master catalogue of all data sources the chatbot will use.

**File to create:** `corpus/corpus.json`

**Exact contents of corpus.json:**

```json
{
  "dynamic": [
    {
      "url": "https://www.sbimf.com/sbimf-scheme-details/sbi-large-cap-fund-(formerly-known-as-sbi-bluechip-fund)-43",
      "scheme_name": "SBI Large Cap Fund",
      "doc_type": "scheme_page",
      "source_type": "html",
      "scrape_frequency": "daily"
    },
    {
      "url": "https://www.sbimf.com/sbimf-scheme-details/sbi-flexicap-fund-39",
      "scheme_name": "SBI Flexicap Fund",
      "doc_type": "scheme_page",
      "source_type": "html",
      "scrape_frequency": "daily"
    },
    {
      "url": "https://www.sbimf.com/sbimf-scheme-details/sbi-elss-tax-saver-fund-(formerly-known-as-sbi-long-term-equity-fund)-3",
      "scheme_name": "SBI ELSS Tax Saver Fund",
      "doc_type": "scheme_page",
      "source_type": "html",
      "scrape_frequency": "daily"
    },
    {
      "url": "https://www.sbimf.com/sbimf-scheme-details/sbi-small-cap-fund-329",
      "scheme_name": "SBI Small Cap Fund",
      "doc_type": "scheme_page",
      "source_type": "html",
      "scrape_frequency": "daily"
    },
    {
      "url": "https://www.sbimf.com/faq",
      "scheme_name": "general",
      "doc_type": "faq",
      "source_type": "html",
      "scrape_frequency": "daily"
    },
    {
      "url": "https://online.sbimf.com/statement",
      "scheme_name": "general",
      "doc_type": "statement_guide",
      "source_type": "html",
      "scrape_frequency": "daily"
    },
    {
      "url": "https://investor.sebi.gov.in/riskometer.html",
      "scheme_name": "general",
      "doc_type": "riskometer_guide",
      "source_type": "html",
      "scrape_frequency": "daily"
    }
  ],
  "static": [
    {
      "url": "https://www.sbimf.com/docs/default-source/scheme-factsheets/sbi-largecap-fund-factsheet-february-2026.pdf",
      "scheme_name": "SBI Large Cap Fund",
      "doc_type": "factsheet",
      "source_type": "pdf",
      "scrape_frequency": "manual"
    },
    {
      "url": "https://www.sbimf.com/docs/default-source/sif-forms/sid---sbi-large-cap-fund-(formerly-known-as-bluechip-fund).pdf",
      "scheme_name": "SBI Large Cap Fund",
      "doc_type": "sid",
      "source_type": "pdf",
      "scrape_frequency": "manual"
    },
    {
      "url": "https://www.sbimf.com/docs/default-source/sif-forms/kim---sbi-large-cap-fund-(formerly-known-as-bluechip-fund).pdf",
      "scheme_name": "SBI Large Cap Fund",
      "doc_type": "kim",
      "source_type": "pdf",
      "scrape_frequency": "manual"
    },
    {
      "url": "https://www.sbimf.com/docs/default-source/scheme-factsheets/sbi-flexicap-fund-factsheet-february-2026.pdf",
      "scheme_name": "SBI Flexicap Fund",
      "doc_type": "factsheet",
      "source_type": "pdf",
      "scrape_frequency": "manual"
    },
    {
      "url": "https://www.sbimf.com/docs/default-source/sif-forms/sid---sbi-flexicap-fund.pdf",
      "scheme_name": "SBI Flexicap Fund",
      "doc_type": "sid",
      "source_type": "pdf",
      "scrape_frequency": "manual"
    },
    {
      "url": "https://www.sbimf.com/docs/default-source/sif-forms/kim---sbi-flexicap-fund.pdf",
      "scheme_name": "SBI Flexicap Fund",
      "doc_type": "kim",
      "source_type": "pdf",
      "scrape_frequency": "manual"
    },
    {
      "url": "https://www.sbimf.com/docs/default-source/scheme-factsheets/sbi-elss-tax-saver-fund-factsheet-february-2026.pdf",
      "scheme_name": "SBI ELSS Tax Saver Fund",
      "doc_type": "factsheet",
      "source_type": "pdf",
      "scrape_frequency": "manual"
    },
    {
      "url": "https://www.sbimf.com/docs/default-source/sif-forms/sid---sbi-elss-tax-saver-fund.pdf",
      "scheme_name": "SBI ELSS Tax Saver Fund",
      "doc_type": "sid",
      "source_type": "pdf",
      "scrape_frequency": "manual"
    },
    {
      "url": "https://www.sbimf.com/docs/default-source/sif-forms/kim---sbi-elss-tax-saver-fund-(formerly-known-as-sbi-long-term-equity-fund).pdf",
      "scheme_name": "SBI ELSS Tax Saver Fund",
      "doc_type": "kim",
      "source_type": "pdf",
      "scrape_frequency": "manual"
    },
    {
      "url": "https://www.sbimf.com/docs/default-source/scheme-factsheets/sbi-small-cap-fund-factsheet-february-2026.pdf",
      "scheme_name": "SBI Small Cap Fund",
      "doc_type": "factsheet",
      "source_type": "pdf",
      "scrape_frequency": "manual"
    },
    {
      "url": "https://www.sbimf.com/docs/default-source/sif-forms/sid---sbi-small-cap-fund.pdf",
      "scheme_name": "SBI Small Cap Fund",
      "doc_type": "sid",
      "source_type": "pdf",
      "scrape_frequency": "manual"
    },
    {
      "url": "https://www.sbimf.com/docs/default-source/sif-forms/kim---sbi-small-cap-fund.pdf",
      "scheme_name": "SBI Small Cap Fund",
      "doc_type": "kim",
      "source_type": "pdf",
      "scrape_frequency": "manual"
    }
  ]
}
```

**Completion checklist:**
- [ ] corpus/corpus.json exists
- [ ] "dynamic" array has 7 HTML sources
- [ ] "static" array has 12 PDF sources
- [ ] All 4 schemes represented in both arrays

---

## PHASE 1.5 — SOURCE CLASSIFICATION ROUTER

**Purpose:** Single entry point that reads corpus.json and routes each source to the correct pipeline — HTML scraper or PDF ingestor.

**File to create:** `ingestion/router.py`

**Exact code:**

```python
import json
import argparse
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def load_corpus():
    with open("corpus/corpus.json", "r") as f:
        return json.load(f)

def run_router(mode: str):
    corpus = load_corpus()
    sources = []

    if mode in ("dynamic", "all"):
        sources.extend(corpus["dynamic"])
    if mode in ("static", "all"):
        sources.extend(corpus["static"])

    logger.info(f"Router starting. Mode: {mode}. Total sources: {len(sources)}")

    for source in sources:
        try:
            if source["source_type"] == "html":
                from ingestion.phase_2_scraper.scraper import scrape_url
                scrape_url(source)
            elif source["source_type"] == "pdf":
                from ingestion.phase_2_5_pdf_ingestor.pdf_ingestor import ingest_pdf
                ingest_pdf(source)
        except Exception as e:
            logger.error(f"Failed to process {source['url']}: {e}")

    logger.info("Router finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dynamic", "static", "all"], default="dynamic")
    args = parser.parse_args()
    run_router(args.mode)
```

**Completion checklist:**
- [ ] ingestion/router.py exists
- [ ] Accepts --mode argument with choices: dynamic, static, all
- [ ] Routes html sources to scraper, pdf sources to pdf_ingestor
- [ ] Has error handling per source (one failure doesn't stop others)

---

## PHASE 2 — HTML SCRAPER

**Purpose:** Fetch live HTML pages from all dynamic sources, extract clean text, and save with metadata. Runs daily via scheduler.

**Folder:** `ingestion/phase_2_scraper/`

**Files to create:** `scraper.py`, `utils.py`

**What scraper.py does step by step:**
1. Receive a source object from the router (contains url, scheme_name, doc_type).
2. Send HTTP GET request with a proper User-Agent header to avoid blocks.
3. If response is not 200, retry up to 3 times with exponential backoff (2s, 4s, 8s).
4. Parse HTML with BeautifulSoup, remove all `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>` tags.
5. Extract remaining text, strip extra whitespace, normalize line breaks.
6. Build metadata dictionary: url, scheme_name, doc_type, scraped_date (today ISO format), source_type.
7. Generate a safe filename from scheme_name + doc_type + date.
8. Save extracted text as `.txt` in `ingestion/raw/html/`.
9. Save metadata as companion `.json` file with same filename.
10. Log success with filename and character count.

**Exact code for scraper.py:**

```python
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
```

**Note:** `utils.py` can remain empty for now — it exists as a placeholder for future helper functions.

**Completion checklist:**
- [ ] ingestion/phase_2_scraper/scraper.py exists with exact code above
- [ ] ingestion/phase_2_scraper/utils.py exists (can be empty)
- [ ] Uses retry logic with exponential backoff
- [ ] Saves .txt and .json pairs to ingestion/raw/html/
- [ ] Has 2-second delay between scrapes (politeness)

---

## PHASE 2.5 — PDF INGESTOR

**Purpose:** Download PDF documents from official SBI MF sources and extract clean text page by page. One-time manual operation, NOT part of daily scheduler.

**Folder:** `ingestion/phase_2_5_pdf_ingestor/`

**Files to create:** `pdf_ingestor.py`, `utils.py`

**What pdf_ingestor.py does step by step:**
1. Receive a source object from the router (contains url, scheme_name, doc_type).
2. Download the PDF file using requests with streaming enabled.
3. Save the raw PDF to `ingestion/raw/pdf/` with a safe filename.
4. Open the PDF with PyMuPDF (`fitz`).
5. Extract text from each page separately, preserving page boundaries with a `[PAGE N]` marker.
6. If PyMuPDF returns empty text for a page (scanned image), fall back to pdfplumber for that page.
7. Combine all page texts into one document string.
8. Build and save metadata JSON: url, scheme_name, doc_type, page_count, ingestion_date.
9. Save extracted text as `.txt` in `ingestion/raw/pdf/`.
10. Log success with page count and character count.

**Exact code for pdf_ingestor.py:**

```python
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
```

**Note:** `utils.py` can remain empty — placeholder for future helpers.

**Completion checklist:**
- [ ] ingestion/phase_2_5_pdf_ingestor/pdf_ingestor.py exists with exact code
- [ ] ingestion/phase_2_5_pdf_ingestor/utils.py exists (can be empty)
- [ ] Uses PyMuPDF as primary, pdfplumber as fallback
- [ ] Saves .pdf, .txt, and .json to ingestion/raw/pdf/
- [ ] Page boundaries marked with [PAGE N]

---

## PHASE 3 — CHUNKING PIPELINE

**Purpose:** Break all raw text files (from both HTML and PDF) into overlapping chunks suitable for embedding. Each chunk carries full metadata for citation.

**Folder:** `ingestion/phase_3_chunker/`

**File to create:** `chunker.py`

**Key parameters:**
- `chunk_size=512`
- `chunk_overlap=64`
- Separators: `["\n\n", "\n", ". ", " ", ""]`

**What chunker.py does step by step:**
1. Scan both `ingestion/raw/html/` and `ingestion/raw/pdf/` for all `.txt` files.
2. For each `.txt` file, load the corresponding `.json` metadata file.
3. Initialize LangChain `RecursiveCharacterTextSplitter` with chunk_size=512, chunk_overlap=64.
4. Split the document text into chunks.
5. For each chunk, attach metadata: source_url, scheme_name, doc_type, source_type, scraped_date, chunk_index, total_chunks.
6. Generate a unique chunk_id = `{scheme_name}_{doc_type}_{chunk_index}` (slugified).
7. Save all chunks as a single `.json` file in `ingestion/chunks/` named after the source file.
8. Log total chunks created per document and overall.

**Exact code for chunker.py:**

```python
import os
import json
import re
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
CHUNKS_DIR = "ingestion/chunks"
os.makedirs(CHUNKS_DIR, exist_ok=True)

RAW_DIRS = [
    "ingestion/raw/html",
    "ingestion/raw/pdf"
]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "_", text.lower())


def chunk_document(text: str, metadata: dict) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_text(text)
    result = []

    for i, chunk_text in enumerate(chunks):
        chunk_id = slugify(f"{metadata['scheme_name']}_{metadata['doc_type']}_{i}")
        result.append({
            "chunk_id": chunk_id,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "text": chunk_text,
            "metadata": {
                "source_url": metadata.get("url", ""),
                "scheme_name": metadata.get("scheme_name", ""),
                "doc_type": metadata.get("doc_type", ""),
                "source_type": metadata.get("source_type", ""),
                "scraped_date": metadata.get("scraped_date") or metadata.get("ingestion_date", ""),
                "chunk_index": i
            }
        })

    return result


def run_chunker():
    all_chunks_created = 0

    for raw_dir in RAW_DIRS:
        if not os.path.exists(raw_dir):
            continue

        txt_files = [f for f in os.listdir(raw_dir) if f.endswith(".txt")]

        for txt_file in txt_files:
            txt_path = os.path.join(raw_dir, txt_file)
            meta_path = txt_path.replace(".txt", ".json")

            if not os.path.exists(meta_path):
                logger.warning(f"No metadata file for {txt_file}, skipping.")
                continue

            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()

            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            chunks = chunk_document(text, metadata)
            output_filename = txt_file.replace(".txt", "_chunks.json")
            output_path = os.path.join(CHUNKS_DIR, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)

            all_chunks_created += len(chunks)
            logger.info(f"{txt_file} → {len(chunks)} chunks saved to {output_filename}")

    logger.info(f"Chunking complete. Total chunks created: {all_chunks_created}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run_chunker()
```

**Completion checklist:**
- [ ] ingestion/phase_3_chunker/chunker.py exists with exact code
- [ ] Chunk size = 512, overlap = 64
- [ ] Scans both raw/html and raw/pdf directories
- [ ] Each chunk has unique chunk_id and full metadata
- [ ] Output saved to ingestion/chunks/

---

## PHASE 4 — EMBEDDING PIPELINE

**Purpose:** Convert all text chunks into 384-dimensional vector embeddings using the local bge-small-en-v1.5 model. No API cost. No internet required.

**Folder:** `ingestion/phase_4_embedder/`

**File to create:** `embedder.py`

**Critical note:** bge-small-en-v1.5 requires a specific prompt prefix for QUERIES only (not documents). Documents are embedded as-is. The query prefix `"Represent this sentence for searching relevant passages: "` is handled in Phase 7 retriever, NOT here.

**Exact code for embedder.py:**

```python
import os
import json
import logging
import time
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "BAAI/bge-small-en-v1.5"
CHUNKS_DIR = "ingestion/chunks"
EMBEDDINGS_DIR = "ingestion/embeddings"
BATCH_SIZE = 32

os.makedirs(EMBEDDINGS_DIR, exist_ok=True)


def run_embedder():
    logger.info(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    logger.info("Model loaded.")

    chunk_files = [f for f in os.listdir(CHUNKS_DIR) if f.endswith("_chunks.json")]

    if not chunk_files:
        logger.warning("No chunk files found. Run chunker first.")
        return

    total_embedded = 0

    for chunk_file in chunk_files:
        chunk_path = os.path.join(CHUNKS_DIR, chunk_file)

        with open(chunk_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        texts = [chunk["text"] for chunk in chunks]

        start = time.time()
        embeddings = model.encode(
            texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=True,
            normalize_embeddings=True
        )
        elapsed = time.time() - start

        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist()

        output_filename = chunk_file.replace("_chunks.json", "_embeddings.json")
        output_path = os.path.join(EMBEDDINGS_DIR, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        total_embedded += len(chunks)
        logger.info(f"{chunk_file} → {len(chunks)} embeddings in {elapsed:.2f}s → saved to {output_filename}")

    logger.info(f"Embedding complete. Total embedded: {total_embedded}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run_embedder()
```

**Completion checklist:**
- [ ] ingestion/phase_4_embedder/embedder.py exists with exact code
- [ ] Uses BAAI/bge-small-en-v1.5 model
- [ ] Batch size = 32
- [ ] normalize_embeddings=True
- [ ] Output saved to ingestion/embeddings/

---

## PHASE 5 — VECTOR DB INGESTION (CHROMA CLOUD)

**Purpose:** Upload all embeddings and metadata to Chroma Cloud for runtime querying.

**Folder:** `ingestion/phase_5_vector_db/`

**File to create:** `vector_db.py`

**Key details:**
- Collection name: `sbi_mf_rag`
- Uses `upsert()` NOT `add()` — so re-running never creates duplicates
- Batch size: 100
- Uses chunk_id as the Chroma document ID

**Exact code for vector_db.py:**

```python
import os
import json
import logging
from dotenv import load_dotenv
import chromadb

load_dotenv()
logger = logging.getLogger(__name__)

EMBEDDINGS_DIR = "ingestion/embeddings"
COLLECTION_NAME = "sbi_mf_rag"
UPSERT_BATCH_SIZE = 100


def get_chroma_client():
    return chromadb.HttpClient(
        host="api.trychroma.com",
        ssl=True,
        headers={
            "x-chroma-token": os.getenv("CHROMA_API_KEY")
        },
        tenant=os.getenv("CHROMA_TENANT"),
        database=os.getenv("CHROMA_DATABASE")
    )


def run_vector_db_ingest():
    logger.info("Connecting to Chroma Cloud...")
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    logger.info(f"Collection '{COLLECTION_NAME}' ready. Current count: {collection.count()}")

    embedding_files = [f for f in os.listdir(EMBEDDINGS_DIR) if f.endswith("_embeddings.json")]

    if not embedding_files:
        logger.warning("No embedding files found. Run embedder first.")
        return

    total_upserted = 0

    for emb_file in embedding_files:
        emb_path = os.path.join(EMBEDDINGS_DIR, emb_file)

        with open(emb_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        ids, embeddings, metadatas, documents = [], [], [], []

        for chunk in chunks:
            ids.append(chunk["chunk_id"])
            embeddings.append(chunk["embedding"])
            metadatas.append(chunk["metadata"])
            documents.append(chunk["text"])

        for i in range(0, len(ids), UPSERT_BATCH_SIZE):
            batch_ids = ids[i:i + UPSERT_BATCH_SIZE]
            batch_emb = embeddings[i:i + UPSERT_BATCH_SIZE]
            batch_meta = metadatas[i:i + UPSERT_BATCH_SIZE]
            batch_docs = documents[i:i + UPSERT_BATCH_SIZE]

            collection.upsert(
                ids=batch_ids,
                embeddings=batch_emb,
                metadatas=batch_meta,
                documents=batch_docs
            )

        total_upserted += len(ids)
        logger.info(f"{emb_file} → {len(ids)} vectors upserted")

    logger.info(f"Ingest complete. Total upserted: {total_upserted}")
    logger.info(f"Collection now contains {collection.count()} vectors")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run_vector_db_ingest()
```

**Completion checklist:**
- [ ] ingestion/phase_5_vector_db/vector_db.py exists with exact code
- [ ] Uses upsert (not add)
- [ ] Batch size = 100
- [ ] Collection name = sbi_mf_rag
- [ ] Reads API keys from .env

---

## PHASE 6 — SCHEDULER (GITHUB ACTIONS)

**Purpose:** Automate the daily HTML ingestion pipeline via GitHub Actions CRON.

**Important:** The `.github/workflows/` folder must be at the ROOT of your repository, not inside `scheduler/`. The `scheduler/` folder in the project tree is just for documentation reference.

**CRON timing:** 9:15 AM IST = 3:45 AM UTC → cron expression: `45 3 * * 1-5` (weekdays only)

### File 1: `.github/workflows/daily_ingest.yml`

```yaml
name: Daily HTML Ingestion

on:
  schedule:
    - cron: "45 3 * * 1-5"
  workflow_dispatch:

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run HTML scraper
        env:
          CHROMA_API_KEY: ${{ secrets.CHROMA_API_KEY }}
          CHROMA_TENANT: ${{ secrets.CHROMA_TENANT }}
          CHROMA_DATABASE: ${{ secrets.CHROMA_DATABASE }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: python ingestion/router.py --mode dynamic

      - name: Run chunker
        run: python ingestion/phase_3_chunker/chunker.py

      - name: Run embedder
        run: python ingestion/phase_4_embedder/embedder.py

      - name: Upsert to Chroma Cloud
        env:
          CHROMA_API_KEY: ${{ secrets.CHROMA_API_KEY }}
          CHROMA_TENANT: ${{ secrets.CHROMA_TENANT }}
          CHROMA_DATABASE: ${{ secrets.CHROMA_DATABASE }}
        run: python ingestion/phase_5_vector_db/vector_db.py
```

### File 2: `.github/workflows/manual_pdf.yml`

```yaml
name: Manual PDF Ingestion

on:
  workflow_dispatch:

jobs:
  ingest_pdf:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run PDF ingestor
        env:
          CHROMA_API_KEY: ${{ secrets.CHROMA_API_KEY }}
          CHROMA_TENANT: ${{ secrets.CHROMA_TENANT }}
          CHROMA_DATABASE: ${{ secrets.CHROMA_DATABASE }}
        run: python ingestion/router.py --mode static

      - name: Run chunker
        run: python ingestion/phase_3_chunker/chunker.py

      - name: Run embedder
        run: python ingestion/phase_4_embedder/embedder.py

      - name: Upsert to Chroma Cloud
        env:
          CHROMA_API_KEY: ${{ secrets.CHROMA_API_KEY }}
          CHROMA_TENANT: ${{ secrets.CHROMA_TENANT }}
          CHROMA_DATABASE: ${{ secrets.CHROMA_DATABASE }}
        run: python ingestion/phase_5_vector_db/vector_db.py
```

**GitHub Secrets to add:** Go to repo → Settings → Secrets and Variables → Actions → add: `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE`, `GROQ_API_KEY`.

**Completion checklist:**
- [ ] .github/workflows/daily_ingest.yml exists at repo root
- [ ] .github/workflows/manual_pdf.yml exists at repo root
- [ ] Daily runs at 45 3 * * 1-5 (9:15 AM IST, weekdays)
- [ ] Manual PDF is workflow_dispatch only
- [ ] Both workflows use secrets for API keys

---

## PHASE 7 — RETRIEVAL SERVICE

**Purpose:** Given a user query, embed it and find the top 5 most relevant chunks from Chroma Cloud using cosine similarity.

**Folder:** `query/phase_7_retriever/`

**File to create:** `retriever.py`

**Critical:** Query MUST be prefixed with `"Represent this sentence for searching relevant passages: "` — this is required by bge models.

**Key parameters:**
- TOP_K = 5
- MAX_DISTANCE = 0.8 (filter out irrelevant results)
- Model and collection are singletons (load once, reuse)

**Exact code for retriever.py:**

```python
import os
import logging
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()
logger = logging.getLogger(__name__)

MODEL_NAME = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "sbi_mf_rag"
TOP_K = 5
MAX_DISTANCE = 0.8
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_model = None
_collection = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.HttpClient(
            host="api.trychroma.com",
            ssl=True,
            headers={"x-chroma-token": os.getenv("CHROMA_API_KEY")},
            tenant=os.getenv("CHROMA_TENANT"),
            database=os.getenv("CHROMA_DATABASE")
        )
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(query: str) -> list[dict]:
    model = get_model()
    collection = get_collection()

    prefixed_query = QUERY_PREFIX + query
    query_embedding = model.encode(
        [prefixed_query],
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []
    for i in range(len(results["documents"][0])):
        distance = results["distances"][0][i]
        if distance > MAX_DISTANCE:
            continue
        retrieved.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": distance
        })

    logger.info(f"Retrieved {len(retrieved)} relevant chunks for query: '{query[:60]}...'")
    return retrieved
```

**Completion checklist:**
- [ ] query/phase_7_retriever/retriever.py exists with exact code
- [ ] Uses QUERY_PREFIX for bge model
- [ ] TOP_K = 5, MAX_DISTANCE = 0.8
- [ ] Singleton pattern for model and collection
- [ ] Returns list of dicts with text, metadata, distance

---

## PHASE 8 — LLM RESPONSE LAYER

**Purpose:** Take retrieved chunks and user query, build a prompt, call Groq API, return a grounded factual answer.

**Folder:** `query/phase_8_llm/`

**File to create:** `llm_handler.py`

**Key parameters:**
- Model: `llama-3.1-8b-instant`
- max_tokens: 300
- temperature: 0.1 (low = more factual)

**System prompt (exact — do not change):**

```
You are a facts-only mutual fund information assistant for SBI Mutual Fund.
Rules you must follow without exception:
1. Answer ONLY using the provided context. Do not use any external knowledge.
2. Your answer must be maximum 3 sentences.
3. You must include exactly one source citation at the end.
4. Never provide investment advice, recommendations, or performance comparisons.
5. If the context does not contain the answer, say: "This information is not available in the current sources. Please visit https://www.sbimf.com for more details."
6. Never say things like "I think", "I recommend", "you should", "it is better to".
```

**Exact code for llm_handler.py:**

```python
import os
import logging
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
logger = logging.getLogger(__name__)

GROQ_MODEL = "llama-3.1-8b-instant"
MAX_TOKENS = 300
TEMPERATURE = 0.1

SYSTEM_PROMPT = """You are a facts-only mutual fund information assistant for SBI Mutual Fund.
Rules you must follow without exception:
1. Answer ONLY using the provided context. Do not use any external knowledge.
2. Your answer must be maximum 3 sentences.
3. You must include exactly one source citation at the end.
4. Never provide investment advice, recommendations, or performance comparisons.
5. If the context does not contain the answer, say: "This information is not available in the current sources. Please visit https://www.sbimf.com for more details."
6. Never say things like "I think", "I recommend", "you should", "it is better to"."""


def build_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks):
        parts.append(f"[Source {i+1}] {chunk['text']}")
    return "\n\n---\n\n".join(parts)


def get_best_source_url(chunks: list[dict]) -> str:
    if chunks:
        return chunks[0]["metadata"].get("source_url", "https://www.sbimf.com")
    return "https://www.sbimf.com"


def get_scraped_date(chunks: list[dict]) -> str:
    if chunks:
        return chunks[0]["metadata"].get("scraped_date", "unknown")
    return "unknown"


def generate_response(query: str, chunks: list[dict]) -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    context = build_context(chunks)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )

    answer = response.choices[0].message.content.strip()
    source_url = get_best_source_url(chunks)
    scraped_date = get_scraped_date(chunks)

    return {
        "answer": answer,
        "source_url": source_url,
        "scraped_date": scraped_date
    }
```

**Completion checklist:**
- [ ] query/phase_8_llm/llm_handler.py exists with exact code
- [ ] System prompt matches exactly
- [ ] Model = llama-3.1-8b-instant
- [ ] temperature = 0.1, max_tokens = 300

---

## PHASE 9 — REFUSAL HANDLER + CITATION FORMATTER

**Purpose:** Pre-retrieval: check if query is advisory (refuse immediately). Post-response: format with citation and footer.

**Folder:** `query/phase_9_refusal/`

**Files to create:** `refusal_handler.py`, `citation_formatter.py`

**Exact code for refusal_handler.py:**

```python
import re
import logging

logger = logging.getLogger(__name__)

ADVISORY_PATTERNS = [
    r"\bshould i\b",
    r"\bwhich is better\b",
    r"\brecommend\b",
    r"\bbest fund\b",
    r"\bcompare\b",
    r"\bwhich fund\b",
    r"\binvest in\b",
    r"\bworth investing\b",
    r"\bgood investment\b",
    r"\bshould invest\b",
    r"\badvice\b",
    r"\bbetter option\b",
]

REFUSAL_MESSAGE = (
    "I can only provide factual information about SBI Mutual Fund schemes. "
    "I'm not able to offer investment advice, recommendations, or fund comparisons. "
    "For investment guidance, please consult a SEBI-registered financial advisor or visit "
    "https://www.mutualfundssahihai.com for investor education."
)


def is_advisory(query: str) -> bool:
    query_lower = query.lower()
    for pattern in ADVISORY_PATTERNS:
        if re.search(pattern, query_lower):
            logger.info(f"Advisory query detected: '{query[:60]}'")
            return True
    return False


def get_refusal_response() -> dict:
    return {
        "answer": REFUSAL_MESSAGE,
        "source_url": "https://www.mutualfundssahihai.com",
        "scraped_date": "N/A",
        "is_refusal": True
    }
```

**Exact code for citation_formatter.py:**

```python
def format_response(answer: str, source_url: str, scraped_date: str) -> str:
    formatted = answer.strip()
    formatted += f"\n\nSource: {source_url}"
    formatted += f"\nLast updated from sources: {scraped_date}"
    return formatted
```

**Completion checklist:**
- [ ] query/phase_9_refusal/refusal_handler.py exists with exact code
- [ ] query/phase_9_refusal/citation_formatter.py exists with exact code
- [ ] 12 advisory patterns defined
- [ ] Refusal message includes SEBI advisor + mutualfundssahihai.com link

---

## PHASE 10 — FASTAPI LAYER

**Purpose:** Expose the chatbot as a REST API. Handle chat sessions. Apply rate limiting.

**Folder:** `api/phase_10_fastapi/`

**Files to create:** `main.py`, `models.py`, `middleware.py`

**Endpoints:**
- `GET /health` → `{"status": "ok"}`
- `POST /chat` → accepts query + session_id, returns formatted answer

**Rate limit:** 10 requests per minute per IP.

**Exact code for models.py:**

```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    session_id: str = Field(default="default")

class ChatResponse(BaseModel):
    answer: str
    source_url: str
    scraped_date: str
    session_id: str
    is_refusal: bool = False
```

**Exact code for main.py:**

```python
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

from api.phase_10_fastapi.models import ChatRequest, ChatResponse
from query.phase_9_refusal.refusal_handler import is_advisory, get_refusal_response
from query.phase_9_refusal.citation_formatter import format_response
from query.phase_7_retriever.retriever import retrieve
from query.phase_8_llm.llm_handler import generate_response

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="SBI MF RAG Chatbot", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest):
    query = body.query.strip()
    session_id = body.session_id

    if is_advisory(query):
        refusal = get_refusal_response()
        return ChatResponse(
            answer=refusal["answer"],
            source_url=refusal["source_url"],
            scraped_date=refusal["scraped_date"],
            session_id=session_id,
            is_refusal=True
        )

    chunks = retrieve(query)

    if not chunks:
        return ChatResponse(
            answer="This information is not available in the current sources. Please visit https://www.sbimf.com for more details.",
            source_url="https://www.sbimf.com",
            scraped_date="N/A",
            session_id=session_id
        )

    llm_result = generate_response(query, chunks)
    formatted_answer = format_response(
        llm_result["answer"],
        llm_result["source_url"],
        llm_result["scraped_date"]
    )

    return ChatResponse(
        answer=formatted_answer,
        source_url=llm_result["source_url"],
        scraped_date=llm_result["scraped_date"],
        session_id=session_id
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.phase_10_fastapi.main:app", host="0.0.0.0", port=8000, reload=True)
```

**Note:** `middleware.py` can remain empty — CORS is handled in main.py directly.

**Completion checklist:**
- [ ] api/phase_10_fastapi/models.py exists with exact code
- [ ] api/phase_10_fastapi/main.py exists with exact code
- [ ] api/phase_10_fastapi/middleware.py exists (can be empty)
- [ ] Rate limiting = 10/minute
- [ ] CORS allows all origins
- [ ] Query max length = 500 characters

---

## PHASE 11 — UI

**Purpose:** Clean, minimal, mobile-first chat interface. No frameworks. Pure HTML/CSS/JS.

**Folder:** `ui/phase_11_ui/`

**Files to create:** `index.html`, `style.css`, `app.js`

**UI components:**
1. Header: "SBI MF Assistant" + disclaimer badge "Facts-only. No investment advice."
2. Example questions: 3 clickable chips that auto-fill the input.
3. Chat window: user messages (right-aligned), bot messages (left-aligned).
4. Bot messages show: answer text, source link, last updated date.
5. Input bar at bottom with send button.
6. Loading spinner while waiting for API response.
7. Error message if API call fails.

**API call pattern in app.js:**

```javascript
const API_URL = "http://localhost:8000/chat";

async function sendMessage(query) {
    const sessionId = getOrCreateSessionId();
    const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, session_id: sessionId })
    });
    if (!response.ok) throw new Error("API error");
    return await response.json();
}

function getOrCreateSessionId() {
    let id = sessionStorage.getItem("sbi_mf_session");
    if (!id) {
        id = "session_" + Math.random().toString(36).substr(2, 9);
        sessionStorage.setItem("sbi_mf_session", id);
    }
    return id;
}
```

**Note:** The full HTML/CSS/JS implementation is left for Windsurf to generate based on these specifications. The UI must be clean, accessible, and mobile-first. No frameworks or CDN dependencies.

**Completion checklist:**
- [ ] ui/phase_11_ui/index.html exists
- [ ] ui/phase_11_ui/style.css exists
- [ ] ui/phase_11_ui/app.js exists with session management and API call logic
- [ ] Disclaimer visible at all times
- [ ] Example questions are clickable
- [ ] Loading state while waiting for response

---

## RUNNING THE FULL PIPELINE — ORDER OF OPERATIONS

**First time (initial setup):**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Ingest PDFs (one time only)
python ingestion/router.py --mode static

# 3. Run chunker
python ingestion/phase_3_chunker/chunker.py

# 4. Run embedder
python ingestion/phase_4_embedder/embedder.py

# 5. Upsert to Chroma Cloud
python ingestion/phase_5_vector_db/vector_db.py

# 6. Start the API
python api/phase_10_fastapi/main.py

# 7. Open ui/phase_11_ui/index.html in browser
```

**Daily (automated via GitHub Actions):**
HTML scrape → chunk → embed → upsert runs automatically at 9:15 AM IST on weekdays.

---

## DATA FLOW ARCHITECTURE

### HTML Ingestion Pipeline
`corpus.json` → `router.py` (filters `source_type=html`) → `scraper.py` (fetch, clean, save `.txt` + `.json` to `raw/html/`) → `chunker.py` (512 chars, 64 overlap, saves to `chunks/`) → `embedder.py` (bge-small-en-v1.5, documents embedded WITHOUT query prefix, saves to `embeddings/`) → `vector_db.py` (upserts to Chroma Cloud collection `sbi_mf_rag` using `chunk_id` as doc ID)

### PDF Ingestion Pipeline
Same but router filters `source_type=pdf`, `pdf_ingestor.py` downloads PDF, extracts page-by-page with `[PAGE N]` markers using PyMuPDF (pdfplumber fallback for empty pages), saves `.pdf` + `.txt` + `.json` to `raw/pdf/`, then same chunker → embedder → vector_db flow

### Query Pipeline
`POST /chat` → `refusal_handler` checks advisory patterns (if yes, return refusal immediately) → `retriever.py` prefixes query with `"Represent this sentence for searching relevant passages: "`, embeds it, queries Chroma top 5, filters distance > 0.8 → if no chunks, return `"not found"` → `llm_handler.py` builds context, calls Groq (llama-3.1-8b-instant, temp=0.1, max_tokens=300) → `citation_formatter` appends source URL + `scraped_date` → return to user

---

## ERROR HANDLING SPECIFICATION

### Scraper
- **non-200 response** → retry 3x with exponential backoff (2s,4s,8s), then skip source
- **Timeout >15s** → same retry logic
- **Empty text <50 chars** → log warning, save but add `"warning":"short_content"` in metadata

### PDF
- **Download fails** → skip PDF
- **PyMuPDF empty page** → pdfplumber fallback
- **Both empty** → `"[PAGE N - EXTRACTION FAILED]"` marker
- **Corrupted PDF** → skip entire file

### Chunker
- **No companion .json** → skip
- **Empty .txt** → skip
- **Zero chunks** → skip

### Embedder
- **Model download fails** → log error with instructions
- **OOM** → reduce batch to 8, then to 1

### Chroma Cloud
- **Connection failed** → raise exception, stop pipeline
- **Upsert timeout** → retry batch once
- **Collection missing** → `get_or_create` handles it

### Retriever runtime
- **Chroma down** → HTTP 503
- **Embedding fails** → HTTP 500
- **Zero results** → `"not found"` response

### Groq runtime
- **429 rate limit** → HTTP 429 message
- **Invalid key** → HTTP 500
- **Timeout >30s** → HTTP 504
- **Empty response** → fallback response

### FastAPI
- **Query >500 chars** → Pydantic 422
- **Rate limit >10/min** → slowapi 429
- **Unhandled exception** → HTTP 500 with logged traceback

---

## EDGE CASES AND GUARDS

1. **Duplicate chunks**: same `chunk_ids` on re-scrape → upsert overwrites (intended behavior)
2. **Hindi queries**: bge is English-only, poor retrieval, fallback response handles gracefully
3. **Stale data**: daily scrape lag is acceptable for V1, `scraped_date` makes it transparent
4. **PDF versioning**: new factsheet URLs need manual `corpus.json` update, old chunks coexist (known issue)
5. **Overlapping chunks**: 64-char overlap is intentional to prevent boundary info loss
6. **Website blocking**: retry logic handles transient failures, persistent blocks need User-Agent rotation
7. **JS-rendered pages**: BeautifulSoup can't parse dynamic content, some pages may return minimal text
8. **Chroma free tier**: ~600 vectors, $5 credit should last months
9. **Concurrency**: singleton model + per-request Groq client, safe for ~10-20 users
10. **Session management**: `session_id` passed through but unused in V1, hook for future multi-turn

---

## KNOWN LIMITATIONS

1. Factsheets are dated February 2026 — newer monthly factsheets require manual re-trigger of the PDF pipeline.
2. bge-small-en-v1.5 is English-only. Hindi queries will have degraded retrieval quality.
3. Chroma Cloud free tier has a $5 usage limit — monitor usage at trychroma.com.
4. SBI MF website may occasionally block scraping — retry logic handles transient failures but persistent blocks require User-Agent rotation.
5. The refusal handler uses keyword matching — sophisticated advisory queries with unusual phrasing may slip through.

---
