"""
Test if wolfonlineshop pagination is working correctly
"""
import requests
from bs4 import BeautifulSoup

# Test a category that likely has multiple pages
url = "https://www.heat-store.de/heizung/heizkoerper/badheizkoerper//"
print(f"Testing pagination on: {url}\n")

# Page 1
response = requests.get(url, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

products_page1 = soup.select('a.product-name')
print(f"Page 1: Found {len(products_page1)} products")

# Check for pagination
next_button = soup.select_one('a.page-next, a[rel="next"]')
print(f"Next button found: {next_button is not None}")

if next_button:
    print(f"Next button href: {next_button.get('href')}")

# Check all page links
page_links = soup.select('nav.pagination a, div.pagination a')
print(f"\nPagination links found: {len(page_links)}")
for link in page_links[:10]:
    text = link.get_text(strip=True)
    href = link.get('href', '')
    print(f"  {text}: {href}")

# Try page 2
print("\n--- Testing Page 2 ---")
page2_url = url + "?p=2"
response2 = requests.get(page2_url, timeout=30)
soup2 = BeautifulSoup(response2.text, 'html.parser')

products_page2 = soup2.select('a.product-name')
print(f"Page 2: Found {len(products_page2)} products")

print(f"\nTotal products from 2 pages: {len(products_page1) + len(products_page2)}")
