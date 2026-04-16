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
        client = chromadb.CloudClient(
            api_key=os.getenv("CHROMA_API_KEY"),
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
