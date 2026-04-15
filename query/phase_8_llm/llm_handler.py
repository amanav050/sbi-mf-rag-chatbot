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
