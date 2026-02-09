"""Test updated wasserpumpe scraper with price fix"""
from wasserpumpe_scraper import WasserpumpeScraper

print("Testing wasserpumpe scraper with 5 products...")
print("="*60)

scraper = WasserpumpeScraper()

# Get just 5 products
success_count = scraper.run(max_products=5)

print("\n" + "="*60)
print(f"Scraped {success_count} products")
print("="*60)

# Show the results
import csv

print("\nResults:")
with open(scraper.get_output_file(), 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, 1):
        print(f"\n{i}. {row['name']}")
        print(f"   Price (gross): {row['price_gross']}")
        print(f"   Price (net): {row['price_net']}")
        print(f"   URL: {row['product_url'][:60]}...")
