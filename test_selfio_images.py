"""Test selfio image extraction"""
from selfio_scraper import SelfioScraper

scraper = SelfioScraper()

print("Getting product URLs...")
urls = scraper.get_product_urls()[:10]

print(f"\nTesting {len(urls)} products for images:\n")

missing_count = 0
success_count = 0

for i, url in enumerate(urls, 1):
    print(f"[{i}/{len(urls)}] {url}")
    product = scraper.scrape_product(url)
    
    if product:
        image = product.get('product_image', '')
        if image:
            print(f"  ✓ Image: {image[:80]}...")
            success_count += 1
        else:
            print(f"  ✗ NO IMAGE!")
            missing_count += 1
    else:
        print(f"  ✗ Failed to scrape")
    print()

print(f"\nResults:")
print(f"  Images found: {success_count}/{len(urls)} ({success_count*100//len(urls)}%)")
print(f"  Images missing: {missing_count}/{len(urls)}")
