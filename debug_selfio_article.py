"""Debug script to find article number in selfio HTML"""
import re
from bs4 import BeautifulSoup

html = open('selfio_missing_article.html', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')

print("Looking for article number patterns...\n")

# Check for productNumber in __NUXT__ data
if '__NUXT__' in html:
    print("Found __NUXT__ data")
    # Try to find productNumber
    patterns = [
        r'productNumber["\']?\s*:\s*["\']([^"\']+)',
        r'sku["\']?\s*:\s*["\']([^"\']+)',
        r'articleNumber["\']?\s*:\s*["\']([^"\']+)',
        r'itemNumber["\']?\s*:\s*["\']([^"\']+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f"  Pattern '{pattern}': {matches[:5]}")

# Check visible text for "Artikel" or "Art.-Nr."
print("\nSearching visible text for article number labels...")
text = soup.get_text()
lines = text.split('\n')
for i, line in enumerate(lines):
    if any(keyword in line.lower() for keyword in ['artikel', 'art.-nr', 'art.nr', 'item number', 'bestellnummer']):
        print(f"  Line {i}: {line.strip()[:100]}")
        if i+1 < len(lines):
            print(f"    Next: {lines[i+1].strip()[:100]}")

# Check for data attributes
print("\nChecking for data attributes...")
for tag in soup.find_all(attrs={'data-product-number': True}):
    print(f"  Found data-product-number: {tag.get('data-product-number')}")

for tag in soup.find_all(attrs={'data-sku': True}):
    print(f"  Found data-sku: {tag.get('data-sku')}")

# Check meta tags
print("\nChecking meta tags...")
for meta in soup.find_all('meta'):
    if meta.get('property') or meta.get('name'):
        prop = meta.get('property') or meta.get('name')
        if any(keyword in prop.lower() for keyword in ['sku', 'product', 'article']):
            print(f"  {prop}: {meta.get('content', 'N/A')}")
