"""Test wasserpumpe to find API or product data"""
import cloudscraper
from bs4 import BeautifulSoup
import json
import re

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

# Try the main shop page
url = 'https://www.wasserpumpe.de/pumpen.html'
print(f'Fetching: {url}')
response = scraper.get(url, timeout=30)

print(f'Status: {response.status_code}')
print(f'Content length: {len(response.text)}')

soup = BeautifulSoup(response.text, 'html.parser')

# Look for JSON data in script tags
print('\n' + '='*60)
print('Looking for JSON data in script tags...')
print('='*60)

scripts = soup.find_all('script')
for i, script in enumerate(scripts):
    script_text = script.string if script.string else ''
    
    # Look for product data
    if 'product' in script_text.lower() and ('price' in script_text.lower() or 'sku' in script_text.lower()):
        print(f'\nScript {i} contains product data:')
        print(script_text[:500])
        print('...')

# Look for Vue.js data
print('\n' + '='*60)
print('Looking for Vue.js data attributes...')
print('='*60)

# Check for data attributes
for elem in soup.find_all(attrs={'data-product': True}):
    print(f'Found data-product: {elem.get("data-product")[:200]}')

for elem in soup.find_all(attrs={'data-price': True}):
    print(f'Found data-price: {elem.get("data-price")}')

# Check the page structure
print('\n' + '='*60)
print('Page structure:')
print('='*60)

# Look for main content div
main_divs = soup.find_all('div', {'id': re.compile(r'app|main|content|products')})
for div in main_divs[:3]:
    print(f'Found div with id: {div.get("id")}')
    print(f'  Classes: {div.get("class")}')
    print(f'  Children: {len(list(div.children))}')

# Try to find actual product pages by checking sitemap more carefully
print('\n' + '='*60)
print('Checking sitemap for product patterns...')
print('='*60)

sitemap_url = 'https://www.wasserpumpe.de/sitemap.xml'
response = scraper.get(sitemap_url, timeout=30)
soup = BeautifulSoup(response.text, 'xml')

urls = soup.find_all('loc')
print(f'Total URLs in sitemap: {len(urls)}')

# Analyze URL patterns
url_patterns = {}
for url_tag in urls[:50]:  # Check first 50
    url = url_tag.text.strip()
    path = url.replace('https://www.wasserpumpe.de/', '').replace('https://wasserpumpe.de/', '')
    
    # Count slashes and dashes
    slashes = path.count('/')
    dashes = path.count('-')
    
    pattern = f'{slashes} slashes, {dashes} dashes'
    if pattern not in url_patterns:
        url_patterns[pattern] = []
    url_patterns[pattern].append(url)

print('\nURL patterns found:')
for pattern, urls in url_patterns.items():
    print(f'\n{pattern}: {len(urls)} URLs')
    print(f'  Examples: {urls[:3]}')
