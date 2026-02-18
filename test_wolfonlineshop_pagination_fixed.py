"""
Test wolfonlineshop pagination is working
"""
from wolfonlineshop_scraper import WolfonlineshopScraper

print("="*70)
print("TESTING WOLFONLINESHOP PAGINATION")
print("="*70)
print("\nTesting with a category that has multiple pages\n")

scraper = WolfonlineshopScraper()

# Manually test just one category that should have multiple pages
# We'll override get_product_urls to test just one category
import requests
from bs4 import BeautifulSoup

category_url = "https://www.heat-store.de/heizung/heizkoerper/badheizkoerper//"
print(f"Testing category: {category_url}\n")

product_urls = []
seen = set()
page = 1

while True:
    if page == 1:
        page_url = category_url
    else:
        page_url = f"{category_url}?p={page}"
    
    print(f"Scraping page {page}: {page_url}")
    
    response = scraper.make_request(page_url)
    if not response:
        break
    
    soup = scraper.parse_html(response.text)
    
    # Find products
    product_links = soup.select('a.product-name')
    
    page_products = 0
    for link in product_links:
        href = link.get('href', '')
        if href and href not in seen:
            seen.add(href)
            product_urls.append(href)
            page_products += 1
    
    print(f"  Found {page_products} new products (total: {len(product_urls)})")
    
    # Check for next page
    next_button = soup.select_one('li.page-item.page-next:not(.disabled)')
    print(f"  Next button exists: {next_button is not None}")
    
    if not next_button or page_products == 0:
        print(f"  No more pages")
        break
    
    page += 1
    
    if page > 5:  # Safety limit for testing
        print("  Reached test limit of 5 pages")
        break

print("\n" + "="*70)
print("PAGINATION TEST RESULTS")
print("="*70)
print(f"Total pages scraped: {page}")
print(f"Total products found: {len(product_urls)}")
print(f"Expected: More than 24 (1 page worth)")
print(f"Status: {'✓ PASS - Pagination working!' if len(product_urls) > 24 else '✗ FAIL - Only got 1 page'}")
print("="*70)
