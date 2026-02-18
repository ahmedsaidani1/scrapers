"""
Debug why wolfonlineshop is finding 0 products now
"""
import requests
from bs4 import BeautifulSoup

# Test a URL that should have products
url = "https://www.heat-store.de/heizung/heizkoerper/badheizkoerper//"
print(f"Testing: {url}\n")

# Try with basic requests
response = requests.get(url, timeout=30)
print(f"Status: {response.status_code}")
print(f"Response length: {len(response.text)}")

soup = BeautifulSoup(response.text, 'html.parser')

# Check for products
products = soup.select('a.product-name')
print(f"\nProducts found with 'a.product-name': {len(products)}")

if products:
    for i, prod in enumerate(products[:3], 1):
        print(f"{i}. {prod.get_text(strip=True)[:60]}")
else:
    print("\nNo products found! Checking if page loaded correctly...")
    
    # Check if we got a valid page
    title = soup.select_one('title')
    print(f"Page title: {title.get_text() if title else 'No title'}")
    
    # Check for any product-related elements
    print("\nLooking for any product elements...")
    product_boxes = soup.select('div.product-box, div.product-item, div.cms-element-product-listing')
    print(f"Product boxes/items: {len(product_boxes)}")
    
    # Check if JavaScript is required
    scripts = soup.find_all('script')
    print(f"Script tags: {len(scripts)}")
    
    # Look for product data in JSON
    for script in scripts:
        if script.string and 'product' in script.string.lower():
            print("\nFound script with 'product' keyword")
            print(script.string[:200])
            break

# Save for inspection
with open('wolfonlineshop_debug_issue.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("\n✓ Saved HTML to wolfonlineshop_debug_issue.html")
