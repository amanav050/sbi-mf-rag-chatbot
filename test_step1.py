import sys
sys.path.append('.')
from ingestion.phase_2_scraper.scraper import scrape_url

source = {
    'url': 'https://www.sbimf.com/faq',
    'scheme_name': 'general',
    'doc_type': 'faq',
    'source_type': 'html'
}

print('Testing HTML scraping...')
scrape_url(source)
print('Scraping completed')
