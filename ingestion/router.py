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
