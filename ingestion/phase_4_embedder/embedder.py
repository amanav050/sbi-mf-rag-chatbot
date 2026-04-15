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
