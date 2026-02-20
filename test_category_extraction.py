"""Test category extraction for all scrapers"""

print("Testing category extraction...\n")

# Test wasserpumpe
print("="*60)
print("WASSERPUMPE")
print("="*60)
from wasserpumpe_scraper import WasserpumpeScraper
s = WasserpumpeScraper()
urls = s.get_product_urls(max_urls=2)
if urls:
    for url in urls[:2]:
        p = s.scrape_product(url)
        if p:
            print(f"Product: {p['name'][:40]}...")
            print(f"Category: '{p.get('category', 'N/A')}'")
            print()

# Test sanundo
print("\n" + "="*60)
print("SANUNDO")
print("="*60)
from sanundo_scraper import SanundoScraper
s2 = SanundoScraper()
urls2 = s2.get_product_urls()
if urls2:
    for url in urls2[:2]:
        p = s2.scrape_product(url)
        if p:
            print(f"Product: {p['name'][:40]}...")
            print(f"Category: '{p.get('category', 'N/A')}'")
            print()

print("\nDone!")
