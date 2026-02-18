"""
Test the fixed pumpe24 scraper with subcategory support
"""
from pumpe24_scraper import Pumpe24Scraper

print("="*70)
print("TESTING FIXED PUMPE24 SCRAPER")
print("="*70)
print("\nTesting with 100 products to verify subcategory scraping works\n")

scraper = Pumpe24Scraper()

# Test with 100 products
success_count = scraper.run(max_products=100, concurrent_workers=10)

print("\n" + "="*70)
print("TEST RESULTS")
print("="*70)
print(f"Products scraped: {success_count}")
print(f"Expected: 100 (or close to it)")
print(f"Status: {'✓ PASS - Subcategories working!' if success_count >= 90 else '✗ FAIL'}")
print("="*70)
