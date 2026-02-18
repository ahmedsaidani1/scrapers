"""
Debug pumpen-heizung.de homepage to find categories
"""
import requests
from bs4 import BeautifulSoup

base_url = "https://pumpen-heizung.de"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print("Checking homepage...")
response = requests.get(base_url, headers=headers, timeout=30)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'html.parser')

# Find all links
all_links = soup.select('a[href]')
print(f"Total links on homepage: {len(all_links)}\n")

# Categorize links
categories = []
products = []
other = []

for link in all_links:
    href = link.get('href', '').strip()
    if not href or href.startswith('#') or href.startswith('javascript:'):
        continue
    
    # Make absolute
    if href.startswith('/'):
        href = base_url + href
    elif not href.startswith('http'):
        continue
    
    if 'pumpen-heizung.de' not in href:
        continue
    
    # Skip common non-product pages
    skip_parts = ['/impressum', '/datenschutz', '/agb', '/kontakt', '/warenkorb', '/account']
    if any(skip in href.lower() for skip in skip_parts):
        continue
    
    # Categorize by URL structure
    path = href.replace(base_url, '')
    slash_count = path.count('/')
    
    if slash_count <= 2 and path.endswith('.html'):
        categories.append(href)
    elif slash_count > 2 and path.endswith('.html'):
        products.append(href)
    else:
        other.append(href)

# Remove duplicates
categories = list(set(categories))
products = list(set(products))

print(f"Potential categories: {len(categories)}")
print(f"Potential products: {len(products)}")
print(f"Other links: {len(other)}\n")

if categories:
    print("First 10 category URLs:")
    for url in categories[:10]:
        print(f"  {url}")
    
    # Test first category
    test_cat = categories[0]
    print(f"\n{'='*80}")
    print(f"Testing category: {test_cat}")
    print('='*80)
    
    response = requests.get(test_cat, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for products
    product_items = soup.select('.product-item, .product, article.product')
    print(f"Products found: {len(product_items)}")
    
    # Check for pagination
    pagination = soup.select('.pagination, .pager, .pages')
    print(f"Pagination elements: {len(pagination)}")
    
    if pagination:
        page_links = soup.select('.pagination a, .pager a, .pages a')
        print(f"Page links: {len(page_links)}")
        if page_links:
            print("Sample page links:")
            for link in page_links[:5]:
                print(f"  {link.get('href', 'N/A')}")
    
    # Save
    with open('pumpenheizung_category_test.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("Saved to: pumpenheizung_category_test.html")

if products:
    print(f"\nFirst 10 product URLs:")
    for url in products[:10]:
        print(f"  {url}")
