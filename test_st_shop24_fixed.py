"""
Test the fixed st_shop24 scraper with pagination
"""
from st_shop24_scraper import StShop24Scraper

scraper = StShop24Scraper()

# Test with first 5 categories to see pagination working
print("Testing st_shop24 scraper with pagination...")
product_urls = scraper.get_product_urls(max_urls=100)

print(f"\nTotal products found: {len(product_urls)}")
print(f"\nFirst 10 URLs:")
for url in product_urls[:10]:
    print(f"  {url}")
