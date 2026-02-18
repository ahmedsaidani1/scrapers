"""
Debug pumpe24 structure to find where products actually are
"""
import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
        "mobile": False,
    }
)

# Test the main pumps category
url = "https://www.pumpe24.de/pumpen.html"
print(f"Fetching: {url}\n")

response = scraper.get(url, timeout=30)
print(f"Status: {response.status_code}")

soup = BeautifulSoup(response.text, 'html.parser')

# Look for subcategories
print("\n=== SUBCATEGORIES ===")
subcategories = soup.select('div.category-item a.category-item-link')
print(f"Found {len(subcategories)} subcategories")
for i, cat in enumerate(subcategories[:5], 1):
    print(f"{i}. {cat.get_text(strip=True)} -> {cat.get('href')}")

# Look for products
print("\n=== PRODUCTS ON THIS PAGE ===")
products = soup.select('a.product-item-link')
print(f"Found {len(products)} product links")
for i, prod in enumerate(products[:5], 1):
    print(f"{i}. {prod.get_text(strip=True)} -> {prod.get('href')}")

# Check pagination
print("\n=== PAGINATION ===")
pagination = soup.select('div.pages a.page')
print(f"Found {len(pagination)} page links")
for page in pagination[:5]:
    print(f"  {page.get_text(strip=True)} -> {page.get('href')}")

# Check toolbar
print("\n=== TOOLBAR INFO ===")
toolbar = soup.select_one('p.toolbar-amount')
if toolbar:
    print(f"Toolbar text: {toolbar.get_text(strip=True)}")

# Save HTML for inspection
with open('pumpe24_debug.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("\n✓ Saved HTML to pumpe24_debug.html")
