"""
Test scraping just a few categories to debug the 0 products issue
"""
from wolfonlineshop_scraper import WolfonlineshopScraper

# Create scraper but override categories to test just a few
scraper = WolfonlineshopScraper()

# Test just these problematic categories
scraper.all_categories = [
    f"{scraper.base_url}/heizung//",
    f"{scraper.base_url}/heizung/fussbodenheizung//",
    f"{scraper.base_url}/heizung/gas-heizung//",
    f"{scraper.base_url}/heizung/heizkoerper//",
]

print(f"Testing {len(scraper.all_categories)} categories...")
product_urls = scraper.get_product_urls(max_urls=200)

print(f"\nTotal products found: {len(product_urls)}")
print(f"\nFirst 10 URLs:")
for url in product_urls[:10]:
    print(f"  {url}")
