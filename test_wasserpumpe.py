"""Test wasserpumpe price extraction"""
import cloudscraper
from bs4 import BeautifulSoup

# Test a specific product URL
url = 'https://wasserpumpe.de/tauchpumpe'
scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

response = scraper.get(url, timeout=30)
print(f'Status: {response.status_code}')
print(f'URL: {response.url}')
print('='*60)

soup = BeautifulSoup(response.text, 'html.parser')

# Try to find price elements
print('Looking for price elements...')
print('='*60)

# Check various price selectors
selectors = [
    'span.price',
    'span[itemprop="price"]',
    'div.product-info-price span.price',
    'meta[itemprop="price"]',
    'div.price-box',
    'span.price-wrapper',
    'div.product-price',
    'div.price',
    'span.regular-price'
]

for selector in selectors:
    elements = soup.select(selector)
    if elements:
        print(f'Found with {selector}:')
        for elem in elements[:3]:
            if elem.name == 'meta':
                print(f'  Content: {elem.get("content", "")}')
            else:
                print(f'  Text: {elem.get_text(strip=True)[:100]}')
        print()

# Check if it's a category page
h1 = soup.select_one('h1')
if h1:
    print(f'Page title: {h1.get_text(strip=True)}')

# Look for product listings
products = soup.select('div.product-item, li.product-item, div.item')
print(f'\nFound {len(products)} product items on page')

# Check page structure
print('\n' + '='*60)
print('Checking if this is a product page or category page...')
print('='*60)

# Look for product-specific elements
product_indicators = [
    ('div.product-info-main', 'Product info main'),
    ('div.product-view', 'Product view'),
    ('button[type="submit"].tocart', 'Add to cart button'),
    ('div.product-add-form', 'Product add form')
]

for selector, name in product_indicators:
    if soup.select_one(selector):
        print(f'✓ Found: {name}')
    else:
        print(f'✗ Not found: {name}')

# Save a snippet of HTML for inspection
print('\n' + '='*60)
print('HTML snippet (first 2000 chars):')
print('='*60)
print(response.text[:2000])
