"""
Debug ST-Shop24 sitemap to find actual URLs
"""
import requests
from bs4 import BeautifulSoup

sitemap_url = "https://st-shop24.de/sitemap.xml"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print("Fetching sitemap...")
response = requests.get(sitemap_url, headers=headers, timeout=30)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'xml')
locs = soup.find_all('loc')

print(f"Total URLs in sitemap: {len(locs)}\n")

# Categorize URLs
categories = []
products = []
other = []

for loc in locs:
    url = loc.text.strip()
    slash_count = url.count('/')
    
    if url.endswith('.html'):
        if slash_count <= 4:
            categories.append(url)
        else:
            products.append(url)
    else:
        other.append(url)

print(f"Categories (<=4 slashes, .html): {len(categories)}")
print(f"Products (>4 slashes, .html): {len(products)}")
print(f"Other: {len(other)}\n")

print("First 10 category URLs:")
for url in categories[:10]:
    print(f"  {url}")

print("\nFirst 10 product URLs:")
for url in products[:10]:
    print(f"  {url}")

# Test a real category URL
if categories:
    test_url = categories[0]
    print(f"\n{'='*80}")
    print(f"Testing first category: {test_url}")
    print('='*80)
    
    response = requests.get(test_url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for products
    products_found = soup.select('.product-item')
    print(f"Products: {len(products_found)}")
    
    # Check pagination
    pagination = soup.select('.pages .item')
    print(f"Pagination items: {len(pagination)}")
    
    # Save
    with open('st_shop24_category_test.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("Saved to: st_shop24_category_test.html")
