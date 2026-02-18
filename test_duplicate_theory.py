"""
Test if parent categories include all subcategory products
"""
from wolfonlineshop_scraper import WolfonlineshopScraper
import time

scraper = WolfonlineshopScraper()

# Scrape parent first, then child
print("Step 1: Scraping parent category (heizung)...")
parent_url = "https://www.heat-store.de/heizung//"
seen = set()

# Get first 3 pages from parent
for page in range(1, 4):
    if page == 1:
        url = parent_url
    else:
        url = f"{parent_url}?p={page}"
    
    response = scraper.make_request(url)
    if response:
        soup = scraper.parse_html(response.text)
        products = soup.select('a.product-name')
        for p in products:
            href = p.get('href', '')
            if href and href not in seen:
                seen.add(href)
        print(f"  Page {page}: {len(products)} products, {len(seen)} total unique")
    time.sleep(0.5)

print(f"\nParent has {len(seen)} unique products in first 3 pages")

# Now try child category
print("\nStep 2: Scraping child category (fussbodenheizung)...")
child_url = "https://www.heat-store.de/heizung/fussbodenheizung//"
child_new = 0
child_duplicates = 0

response = scraper.make_request(child_url)
if response:
    soup = scraper.parse_html(response.text)
    products = soup.select('a.product-name')
    print(f"  Child page 1 has {len(products)} products")
    
    for p in products:
        href = p.get('href', '')
        if href:
            if href in seen:
                child_duplicates += 1
            else:
                child_new += 1
                seen.add(href)

print(f"\nChild category results:")
print(f"  New products: {child_new}")
print(f"  Duplicates (already in parent): {child_duplicates}")
print(f"  Total unique after both: {len(seen)}")
