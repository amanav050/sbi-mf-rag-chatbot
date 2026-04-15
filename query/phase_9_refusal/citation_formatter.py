def format_response(answer: str, source_url: str, scraped_date: str) -> str:
    formatted = answer.strip()
    formatted += f"\n\nSource: {source_url}"
    formatted += f"\nLast updated from sources: {scraped_date}"
    return formatted
