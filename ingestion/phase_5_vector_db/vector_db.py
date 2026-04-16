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
    return chromadb.CloudClient(
        api_key=os.getenv("CHROMA_API_KEY"),
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
