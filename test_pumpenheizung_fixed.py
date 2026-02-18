"""
Test the fixed pumpenheizung scraper
"""
from pumpenheizung_scraper import PumpenheizungScraper

scraper = PumpenheizungScraper()

print("Testing pumpenheizung scraper with new approach...")
product_urls = scraper.get_product_urls(max_urls=100)

print(f"\nTotal products found: {len(product_urls)}")
print(f"\nFirst 10 URLs:")
for url in product_urls[:10]:
    print(f"  {url}")
