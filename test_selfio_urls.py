"""
Quick test to see what URLs are in selfio sitemap - find actual products
"""
import requests
import gzip
from bs4 import BeautifulSoup

sitemap_url = "https://www.selfio.de/sitemap.xml"

print("Fetching main sitemap...")
response = requests.get(sitemap_url, timeout=30)
soup = BeautifulSoup(response.text, 'xml')
sitemap_locs = soup.find_all('loc')

print(f"Found {len(sitemap_locs)} sub-sitemaps")

# Get first sitemap (the big one)
first_sitemap_url = sitemap_locs[0].text.strip()
print(f"\nFetching: {first_sitemap_url}")

gz_response = requests.get(first_sitemap_url, timeout=30)
decompressed = gzip.decompress(gz_response.content).decode('utf-8')
sitemap_soup = BeautifulSoup(decompressed, 'xml')
urls = sitemap_soup.find_all('loc')

print(f"Found {len(urls)} URLs total")

# Look for URLs that look like products (have product-like paths)
# Products typically have format: /category/subcategory/product-name
products = []

for url_tag in urls:
    url = url_tag.text.strip()
    
    # Skip obvious non-products
    if any(x in url for x in ['/blog/', '/presse/', '/aktuelle-meldungen/', '/angebot-anfordern/', 
                               '/rechtliches/', '/ueber-', '/downloads', '/newsletter', '/faq',
                               '/service', '/lieferung', '/impressum', '/agb', '/datenschutz',
                               '/widerrufsbelehrung', '/gewaehrleistung', '/kontakt', '/versandkosten',
                               '/zahlungsmethoden', '/planungsservice/', '/dienstleistung/']):
        continue
    
    # Skip categories (ending with /)
    if url.endswith('/'):
        continue
    
    # Skip homepage and very short URLs
    if url.count('/') < 4:
        continue
    
    products.append(url)

print(f"\nFiltered to {len(products)} potential product URLs")
print(f"\nFirst 50 potential product URLs:")
for i, url in enumerate(products[:50], 1):
    print(f"{i}. {url}")
