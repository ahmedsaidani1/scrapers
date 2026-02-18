"""
Debug heat-store.de to find the correct product selectors
"""
import requests
from bs4 import BeautifulSoup

# Test a category that should have products
url = "https://www.heat-store.de/heizung/heizkoerper/badheizkoerper//"
print(f"Fetching: {url}\n")

response = requests.get(url, timeout=30)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'html.parser')

# Try different selectors
print("=== TRYING DIFFERENT SELECTORS ===\n")

selectors = [
    'a.product-name',
    'a[href$=".html"]',
    'a.product-link',
    'a.product-item',
    'div.product-box a',
    'div.product-item a',
    'a[title]',
]

for selector in selectors:
    links = soup.select(selector)
    print(f"{selector}: {len(links)} links")
    if links:
        for i, link in enumerate(links[:3], 1):
            href = link.get('href', '')
            text = link.get_text(strip=True)[:50]
            print(f"  {i}. {text} -> {href[:80]}")
        print()

# Check for any links ending with .html
print("\n=== ALL LINKS ENDING WITH .html ===")
all_links = soup.find_all('a', href=True)
html_links = [link for link in all_links if link.get('href', '').endswith('.html')]
print(f"Found {len(html_links)} links ending with .html")
for i, link in enumerate(html_links[:10], 1):
    href = link.get('href', '')
    text = link.get_text(strip=True)[:50]
    # Check if it's a product (not a category)
    is_product = '//' not in href
    print(f"{i}. {'[PRODUCT]' if is_product else '[CATEGORY]'} {text}")
    print(f"   {href}")

# Save HTML for inspection
with open('heatstore_category_debug.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("\n✓ Saved HTML to heatstore_category_debug.html")
