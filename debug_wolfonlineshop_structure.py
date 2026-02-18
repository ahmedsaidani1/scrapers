"""
Debug wolfonlineshop/heat-store structure to find all products
"""
import requests
from bs4 import BeautifulSoup

base_url = "https://www.heat-store.de"

# Test a category page
url = f"{base_url}/heizung/heizkoerper/badheizkoerper//"
print(f"Fetching: {url}\n")

response = requests.get(url, timeout=30)
print(f"Status: {response.status_code}")

soup = BeautifulSoup(response.text, 'html.parser')

# Look for products
print("\n=== PRODUCTS ON THIS PAGE ===")
products = soup.select('a.product-name')
print(f"Found {len(products)} with .product-name")

products2 = soup.select('a[href*=".html"]')
print(f"Found {len(products2)} links with .html")

# Check for product boxes
product_boxes = soup.select('div.product-box')
print(f"Found {len(product_boxes)} product boxes")

# Check pagination
print("\n=== PAGINATION ===")
pagination = soup.select('nav.pagination a')
print(f"Found {len(pagination)} pagination links")
for page in pagination[:5]:
    print(f"  {page.get_text(strip=True)} -> {page.get('href')}")

# Check if there's a "next" button
next_btn = soup.select_one('a.page-next')
if next_btn:
    print(f"Next button: {next_btn.get('href')}")

# Look for total product count
print("\n=== PRODUCT COUNT INFO ===")
count_elem = soup.select_one('p.cms-listing-col')
if count_elem:
    print(f"Count element: {count_elem.get_text(strip=True)}")

# Save HTML
with open('wolfonlineshop_debug.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("\n✓ Saved HTML to wolfonlineshop_debug.html")

# Try to find sitemap
print("\n=== CHECKING SITEMAP ===")
sitemap_url = f"{base_url}/sitemap.xml"
try:
    sitemap_response = requests.get(sitemap_url, timeout=10)
    print(f"Sitemap status: {sitemap_response.status_code}")
    if sitemap_response.status_code == 200:
        sitemap_soup = BeautifulSoup(sitemap_response.text, 'xml')
        locs = sitemap_soup.find_all('loc')
        print(f"Found {len(locs)} URLs in sitemap")
        # Check for product URLs
        product_urls = [loc.text for loc in locs if '.html' in loc.text and 'heizung' in loc.text]
        print(f"Product-like URLs: {len(product_urls)}")
        if product_urls:
            print("Sample URLs:")
            for url in product_urls[:5]:
                print(f"  {url}")
except Exception as e:
    print(f"Sitemap error: {e}")
