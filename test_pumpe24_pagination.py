"""
Test pumpe24 pagination - verify it scrapes more than 50 products
"""
from pumpe24_scraper import Pumpe24Scraper

print("="*70)
print("TESTING PUMPE24 PAGINATION")
print("="*70)
print("\nThis will test if pagination works by scraping 100 products")
print("If pagination works, you should see multiple pages being scraped\n")

scraper = Pumpe24Scraper()

# Test with 100 products to verify pagination
success_count = scraper.run(max_products=100, concurrent_workers=10)

print("\n" + "="*70)
print("TEST RESULTS")
print("="*70)
print(f"Products scraped: {success_count}")
print(f"Expected: 100 (or close to it)")
print(f"Status: {'✓ PASS' if success_count >= 90 else '✗ FAIL'}")
print("="*70)
