"""Test how many products the wolf scraper can find"""
from wolf_online_shop_scraper import WolfOnlineShopScraper

scraper = WolfOnlineShopScraper()

print("=" * 60)
print("Testing Wolf-Online-Shop Product Discovery")
print("=" * 60)

# Get all product URLs (no limit)
print("\nDiscovering all products (this may take a few minutes)...")
product_urls = scraper.get_product_urls()

print(f"\n{'='*60}")
print(f"Total products found: {len(product_urls)}")
print(f"{'='*60}")

if product_urls:
    print("\nFirst 10 product URLs:")
    for i, url in enumerate(product_urls[:10], 1):
        print(f"{i}. {url}")
    
    if len(product_urls) > 10:
        print(f"\n... and {len(product_urls) - 10} more products")
    
    print(f"\nLast 5 product URLs:")
    for i, url in enumerate(product_urls[-5:], len(product_urls)-4):
        print(f"{i}. {url}")
else:
    print("\n⚠ No products found!")

print(f"\n{'='*60}")
print("Product discovery complete!")
print(f"{'='*60}")
