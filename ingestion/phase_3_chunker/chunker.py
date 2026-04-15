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
