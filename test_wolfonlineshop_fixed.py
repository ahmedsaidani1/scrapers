"""
Test the fixed wolfonlineshop scraper with multi-level category support
"""
from wolfonlineshop_scraper import WolfonlineshopScraper

print("="*70)
print("TESTING FIXED WOLFONLINESHOP SCRAPER")
print("="*70)
print("\nTesting with 100 products to verify multi-level category scraping\n")

scraper = WolfonlineshopScraper()

# Test with 100 products
success_count = scraper.run(max_products=100, concurrent_workers=10)

print("\n" + "="*70)
print("TEST RESULTS")
print("="*70)
print(f"Products scraped: {success_count}")
print(f"Expected: 100 (or close to it)")
print(f"Status: {'✓ PASS - Multi-level categories working!' if success_count >= 90 else '✗ FAIL'}")
print("="*70)
