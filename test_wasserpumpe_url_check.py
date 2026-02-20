"""
Check if wasserpumpe URLs are being filtered correctly
"""
import sys
sys.path.insert(0, '.')

from wasserpumpe_scraper import WasserpumpeScraper

scraper = WasserpumpeScraper()

test_urls = [
    "https://wasserpumpe.de/hauswasserwerk-mit-druckschalter",  # Category page
    "https://wasserpumpe.de/brunnenpumpe-mit-druckschalter",  # Category page
    "https://wasserpumpe.de/grundfos-scala2-3-45-hauswasserautomat-mit-integriertem-druckbehaelter",  # Real product
]

print("\nTesting URL filtering:\n")
for url in test_urls:
    is_product = scraper._is_product_url(url)
    print(f"URL: {url}")
    print(f"  Is Product: {is_product}")
    print(f"  Length: {len(url.replace('https://wasserpumpe.de/', ''))}")
    print()
