"""
Debug pumpe24 subcategory to find actual products
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

# Test a subcategory
url = "https://www.pumpe24.de/pumpen/gartenpumpen.html"
print(f"Fetching subcategory: {url}\n")

response = scraper.get(url, timeout=30)
print(f"Status: {response.status_code}")

soup = BeautifulSoup(response.text, 'html.parser')

# Look for products
print("\n=== PRODUCTS ON THIS PAGE ===")
products = soup.select('a.product-item-link')
print(f"Found {len(products)} product links")
for i, prod in enumerate(products[:10], 1):
    href = prod.get('href', '')
    text = prod.get_text(strip=True)
    print(f"{i}. {text}")
    print(f"   URL: {href}")
    print(f"   Looks like product: {'/pumpen/' in href and href.count('/') > 3}")

# Check pagination
print("\n=== PAGINATION ===")
next_page = soup.select_one('a.action.next')
if next_page:
    print(f"Next page found: {next_page.get('href')}")
else:
    print("No next page")

pagination = soup.select('div.pages a')
print(f"Found {len(pagination)} page links")

# Check toolbar for product count
print("\n=== TOOLBAR INFO ===")
toolbar = soup.select_one('p.toolbar-amount')
if toolbar:
    print(f"Toolbar text: {toolbar.get_text(strip=True)}")

# Save HTML
with open('pumpe24_subcategory_debug.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("\n✓ Saved HTML to pumpe24_subcategory_debug.html")
