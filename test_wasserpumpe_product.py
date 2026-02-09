"""Test wasserpumpe to find actual product URLs"""
import cloudscraper
from bs4 import BeautifulSoup
import re

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

# Try a category page to find product links
category_url = 'https://www.wasserpumpe.de/tauchpumpe'
print(f'Fetching category: {category_url}')
response = scraper.get(category_url, timeout=30)

soup = BeautifulSoup(response.text, 'html.parser')

# Look for product links
print('\nLooking for product links...')
print('='*60)

# Find all links
all_links = soup.find_all('a', href=True)
product_links = []

for link in all_links:
    href = link.get('href', '')
    
    # Look for product-like URLs
    if 'wasserpumpe.de' in href and not any(skip in href for skip in [
        '/tauchpumpe', '/pumpen', '/zubehoer', '/gartenpumpe',
        'javascript:', '#', '/rechtliches', '/datenschutz', 
        '/impressum', '/uber-uns', '/allgemeine-geschaftsbedingungen'
    ]):
        # Check if it has a product-like pattern (longer path)
        path = href.replace('https://www.wasserpumpe.de/', '').replace('https://wasserpumpe.de/', '')
        if '/' in path or '-' in path:
            product_links.append(href)

# Remove duplicates
product_links = list(set(product_links))

print(f'Found {len(product_links)} potential product links')
print('\nFirst 10 product links:')
for i, link in enumerate(product_links[:10], 1):
    print(f'{i}. {link}')

# Test one product link
if product_links:
    test_url = product_links[0]
    print(f'\n{"="*60}')
    print(f'Testing product URL: {test_url}')
    print('='*60)
    
    response = scraper.get(test_url, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for price
    print('\nLooking for price...')
    price_selectors = [
        'span.price',
        'div.price',
        '[class*="price"]',
        '[itemprop="price"]'
    ]
    
    for selector in price_selectors:
        elements = soup.select(selector)
        if elements:
            print(f'\nFound with {selector}:')
            for elem in elements[:5]:
                text = elem.get_text(strip=True)
                if text and ('€' in text or ',' in text or text.replace('.', '').isdigit()):
                    print(f'  {text}')
    
    # Check page title
    h1 = soup.select_one('h1')
    if h1:
        print(f'\nProduct title: {h1.get_text(strip=True)}')
    
    # Check if it's a product page
    add_to_cart = soup.select_one('button[type="submit"]')
    if add_to_cart:
        print('✓ This appears to be a product page (has add to cart button)')
    else:
        print('✗ This does not appear to be a product page')
