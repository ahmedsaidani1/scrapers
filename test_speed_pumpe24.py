"""
Test speed with pumpe24 - should be faster
"""
import time
from pumpe24_scraper import Pumpe24Scraper

print("="*70)
print("TESTING SPEED WITH PUMPE24.DE")
print("="*70)
print("\nTesting with 50 products...\n")

start_time = time.time()

scraper = Pumpe24Scraper()
success_count = scraper.run(max_products=50, concurrent_workers=10)

elapsed_time = time.time() - start_time

print("\n" + "="*70)
print("TEST RESULTS")
print("="*70)
print(f"Products scraped: {success_count}")
print(f"Time taken: {elapsed_time:.2f} seconds")
if elapsed_time > 0:
    print(f"Speed: {success_count/elapsed_time:.1f} products/second")
print("\n" + "="*70)
print("COMPARISON")
print("="*70)
print(f"Old method (sequential, 2s delay): ~100 seconds")
print(f"New method (concurrent): {elapsed_time:.2f} seconds")
if elapsed_time > 0:
    print(f"Speedup: {100/elapsed_time:.1f}x faster!")
print("="*70)
