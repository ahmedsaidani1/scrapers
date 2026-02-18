"""
Debug wolfonlineshop to find all categories and check pagination
"""
import requests
from bs4 import BeautifulSoup

base_url = "https://www.heat-store.de"

print("=== FINDING ALL CATEGORIES ===\n")

# Start from main navigation
response = requests.get(base_url, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

# Find navigation links
nav_links = soup.select('nav a[href*="/heizung/"]')
print(f"Found {len(nav_links)} navigation links with /heizung/")

categories = set()
for link in nav_links:
    href = link.get('href', '')
    if href and '/heizung/' in href:
        if href.startswith('/'):
            href = base_url + href
        categories.add(href)

print(f"\nUnique categories found: {len(categories)}")
for cat in sorted(categories)[:20]:
    print(f"  {cat}")

# Test pagination on a category with many products
print("\n\n=== TESTING PAGINATION ===")
test_url = f"{base_url}/heizung/heizkoerper/paneelheizkoerper//"
print(f"Testing: {test_url}")

response = requests.get(test_url, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

# Count products
products = soup.select('div.product-box')
print(f"Products on page 1: {len(products)}")

# Look for pagination
pagination_links = soup.select('nav.pagination a, div.pagination a, a.page-link')
print(f"Pagination links found: {len(pagination_links)}")

for link in pagination_links[:10]:
    text = link.get_text(strip=True)
    href = link.get('href', '')
    print(f"  {text} -> {href}")

# Try page 2 manually
print("\n=== TRYING PAGE 2 ===")
page2_patterns = [
    f"{test_url}?p=2",
    f"{test_url}?page=2",
    f"{test_url}/p/2",
]

for pattern in page2_patterns:
    try:
        resp = requests.get(pattern, timeout=10)
        if resp.status_code == 200:
            s = BeautifulSoup(resp.text, 'html.parser')
            prods = s.select('div.product-box')
            if len(prods) > 0 and len(prods) != len(products):
                print(f"✓ Found page 2: {pattern}")
                print(f"  Products: {len(prods)}")
                break
    except:
        pass
