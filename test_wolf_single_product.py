"""Test a single actual product from wolf-online-shop"""
from wolf_online_shop_scraper import WolfOnlineShopScraper

scraper = WolfOnlineShopScraper()

# Test with actual product URL from the HTML
test_url = "https://www.wolf-online-shop.de/Uponor-Smart-Tacker-Nadel-14-20mm-h-40mm-VPE-1000-Stueck::526585.html"

print(f"Testing product: {test_url}")
print("=" * 60)

product_data = scraper.scrape_product(test_url)

if product_data:
    print("\n✓ Successfully scraped product:")
    print("-" * 60)
    for key, value in product_data.items():
        print(f"{key:20s}: {value}")
    print("-" * 60)
else:
    print("\n✗ Failed to scrape product")
