"""Find actual product pages on ST-Shop24"""
import requests
from bs4 import BeautifulSoup

# Get a category page
category_url = "https://st-shop24.de/motoren/baugroesse-b3/2-polig-3000-u-min.html"
print(f"Checking category: {category_url}\n")

r = requests.get(category_url)
soup = BeautifulSoup(r.text, 'html.parser')

# Find all links
all_links = soup.find_all('a', href=True)
product_links = []

for link in all_links:
    href = link.get('href')
    if href and '.html' in href and href.count('/') > 5:
        if href.startswith('/'):
            href = 'https://st-shop24.de' + href
        if href not in product_links:
            product_links.append(href)

print(f"Found {len(product_links)} potential product links")
print("\nSample links:")
for link in product_links[:10]:
    print(f"  {link}")

# Test one of these links
if product_links:
    print(f"\n{'='*60}")
    print("Testing first link as product page:")
    print('='*60)
    test_url = product_links[0]
    print(f"URL: {test_url}\n")
    
    r2 = requests.get(test_url)
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    
    title = soup2.find('h1')
    price = soup2.select_one('.price, .woocommerce-Price-amount')
    sku = soup2.select_one('.sku')
    
    print(f"Title: {title.text.strip() if title else 'None'}")
    print(f"Price: {price.text.strip() if price else 'None'}")
    print(f"SKU: {sku.text.strip() if sku else 'None'}")
    
    # Check if it has product schema
    product_schema = soup2.find('div', {'itemtype': 'http://schema.org/Product'})
    print(f"Has product schema: {bool(product_schema)}")
