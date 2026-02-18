"""
Debug ST-Shop24 structure to understand category hierarchy and pagination
"""
import requests
from bs4 import BeautifulSoup

base_url = "https://st-shop24.de"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Test a category page to see structure
test_urls = [
    "https://st-shop24.de/pumpen.html",
    "https://st-shop24.de/heizung.html",
]

for url in test_urls:
    print(f"\n{'='*80}")
    print(f"Testing: {url}")
    print('='*80)
    
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for products
    products = soup.select('.product-item')
    print(f"Products found with '.product-item': {len(products)}")
    
    # Check for subcategories
    subcats = soup.select('.category-item')
    print(f"Subcategories found with '.category-item': {len(subcats)}")
    
    # Check for pagination
    pagination = soup.select('.pages')
    print(f"Pagination elements: {len(pagination)}")
    
    if pagination:
        pages = soup.select('.pages .item')
        print(f"  Page items: {len(pages)}")
        
        # Check for next button
        next_btn = soup.select_one('.pages .action.next')
        print(f"  Has next button: {next_btn is not None}")
    
    # Save HTML
    filename = url.split('/')[-1].replace('.html', '_debug.html')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"Saved to: {filename}")
