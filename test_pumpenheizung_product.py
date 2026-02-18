"""
Test if these simple URLs are actually product pages
"""
import requests
from bs4 import BeautifulSoup

test_urls = [
    "https://pumpen-heizung.de/Clip",
    "https://pumpen-heizung.de/O-Ring",
    "https://pumpen-heizung.de/Hydromono",
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
    
    # Check for product indicators
    title = soup.select_one('h1, title')
    if title:
        print(f"Title: {title.get_text(strip=True)[:80]}")
    
    # Check for price
    price = soup.select_one('[class*="preis"], [class*="price"]')
    if price:
        print(f"Price found: {price.get_text(strip=True)[:50]}")
    
    # Check for "add to cart"
    cart = soup.select_one('button[class*="cart"], input[value*="Warenkorb"]')
    if cart:
        print(f"Add to cart button: Yes")
    
    # Check for product description
    desc = soup.select_one('[class*="beschreibung"], [class*="description"], [itemprop="description"]')
    if desc:
        print(f"Description found: {desc.get_text(strip=True)[:80]}...")
    
    # Check for JSON-LD
    json_ld = soup.select('script[type="application/ld+json"]')
    if json_ld:
        print(f"JSON-LD scripts: {len(json_ld)}")
        for script in json_ld:
            if 'Product' in script.string:
                print(f"  Contains Product schema: Yes")
                break
