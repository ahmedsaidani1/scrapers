"""Test Actec Solar website structure"""
import requests
from bs4 import BeautifulSoup

categories = [
    'https://www.actec-solar.de/komplettanlagen',
    'https://www.actec-solar.de/balkonkraftwerke',
    'https://www.actec-solar.de/solarmodule',
]

all_product_urls = []

for cat_url in categories:
    print(f"\n=== Testing: {cat_url} ===")
    r = requests.get(cat_url)
    print(f"Status: {r.status_code}")
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Find product cards
    products = soup.find_all(['div', 'article'], class_=lambda x: x and 'product' in str(x).lower())
    print(f"Product elements found: {len(products)}")
    
    # Find all links
    links = soup.find_all('a', href=True)
    
    # Look for product links
    for link in links:
        href = link.get('href')
        text = link.text.strip()[:50]
        
        # Check if it looks like a product
        if any(keyword in href.lower() for keyword in ['komplettanlage', 'balkonkraftwerk', 'solarmodul', 'wechselrichter']):
            if href.startswith('/'):
                full_url = 'https://www.actec-solar.de' + href
            else:
                full_url = href
            
            # Avoid category pages (they usually end with /)
            if not full_url.endswith('/') and full_url not in all_product_urls:
                all_product_urls.append(full_url)
                if len(all_product_urls) <= 5:
                    print(f"  Product: {text[:40]} -> {full_url}")

print(f"\n=== Total unique product URLs found: {len(all_product_urls)} ===")
print("\nFirst 10 URLs:")
for url in all_product_urls[:10]:
    print(f"  {url}")
