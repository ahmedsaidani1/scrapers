"""Test wolfonlineshop category extraction"""
from wolfonlineshop_scraper import WolfonlineshopScraper

s = WolfonlineshopScraper()

test_urls = [
    'https://www.heat-store.de/danfoss-thermot-thermischer-stellantrieb-fussbodenheizung-24v-ac-dc-088h3216.html',
    'https://www.heat-store.de/buderus-logafix-stellantrieb-230-volt-fuer-fussbodenheizung-heizkreisverteiler-hkv.html',
]

for url in test_urls:
    p = s.scrape_product(url)
    if p:
        print(f"Product: {p['name'][:40]}...")
        print(f"Category: {p.get('category', 'N/A')}")
        print(f"URL: {url}")
        print()
