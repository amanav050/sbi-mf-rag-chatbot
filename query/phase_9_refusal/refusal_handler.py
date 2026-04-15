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
