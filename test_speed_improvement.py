"""
Quick test to verify speed improvements with concurrent scraping.
Tests with 100 products to see the performance difference.
"""
import time
from wolfonlineshop_scraper import WolfonlineshopScraper

print("="*70)
print("TESTING SPEED IMPROVEMENTS")
print("="*70)
print("\nThis will scrape 100 products from wolfonlineshop.de")
print("to demonstrate the speed improvement with concurrent scraping.\n")

# Test with concurrent scraping
print("Starting test with 10 concurrent workers...")
print("-"*70)

start_time = time.time()

scraper = WolfonlineshopScraper()
success_count = scraper.run(max_products=100, concurrent_workers=10)

elapsed_time = time.time() - start_time

print("\n" + "="*70)
print("TEST RESULTS")
print("="*70)
print(f"Products scraped: {success_count}")
print(f"Time taken: {elapsed_time:.2f} seconds")
print(f"Speed: {success_count/elapsed_time:.1f} products/second")
print("\n" + "="*70)
print("COMPARISON")
print("="*70)
print(f"Old method (sequential, 2s delay): ~200 seconds")
print(f"New method (concurrent): {elapsed_time:.2f} seconds")
print(f"Speedup: {200/elapsed_time:.1f}x faster!")
print("="*70)
