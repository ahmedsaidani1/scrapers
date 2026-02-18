"""
Debug script to check categories showing 0 products
"""
import requests
from bs4 import BeautifulSoup

# Test a few categories that showed 0 products
test_urls = [
    "https://www.heat-store.de/heizung/brennstoffzelle//",
    "https://www.heat-store.de/heizung/fussbodenheizung//",
    "https://www.heat-store.de/heizung/gas-heizung//",
    "https://www.heat-store.de/heizung/heizkoerper//",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

for url in test_urls:
    print(f"\n{'='*80}")
    print(f"Testing: {url}")
    print('='*80)
    
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for products using the selector we use in scraper
    products = soup.select('a.product-name')
    print(f"Products found with 'a.product-name': {len(products)}")
    
    # Try alternative selectors
    alt_selectors = [
        'div.product-box',
        'div.product-item',
        'a.product-link',
        'div.cms-listing-col',
        'div.product-listing',
    ]
    
    for selector in alt_selectors:
        elements = soup.select(selector)
        if elements:
            print(f"  Found {len(elements)} elements with '{selector}'")
    
    # Check for pagination
    pagination = soup.select('li.page-item')
    print(f"Pagination elements: {len(pagination)}")
    
    # Check for "no products" message
    no_products = soup.select('div.cms-element-text')
    if no_products:
        print(f"Text elements found: {len(no_products)}")
        for elem in no_products[:3]:
            text = elem.get_text(strip=True)[:100]
            if text:
                print(f"  Text: {text}")
    
    # Save HTML for inspection
    filename = url.split('/')[-3] + '_debug.html'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"Saved HTML to: {filename}")
