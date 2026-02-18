"""
Debug wolfonlineshop sitemap structure
"""
import requests
from bs4 import BeautifulSoup

base_url = "https://www.heat-store.de"

print("=== CHECKING SITEMAP STRUCTURE ===\n")

# Check main sitemap
sitemap_url = f"{base_url}/sitemap.xml"
response = requests.get(sitemap_url, timeout=10)
print(f"Main sitemap status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'xml')
locs = soup.find_all('loc')
print(f"Found {len(locs)} URLs in main sitemap:")
for loc in locs:
    print(f"  {loc.text}")

# Check if there are sitemap indexes
print("\n=== CHECKING FOR SITEMAP INDEXES ===")
for loc in locs:
    url = loc.text
    if 'sitemap' in url.lower():
        print(f"\nFetching sub-sitemap: {url}")
        try:
            sub_response = requests.get(url, timeout=10)
            sub_soup = BeautifulSoup(sub_response.text, 'xml')
            sub_locs = sub_soup.find_all('loc')
            print(f"  Found {len(sub_locs)} URLs")
            
            # Count product URLs
            product_urls = [l.text for l in sub_locs if '.html' in l.text]
            print(f"  Product URLs (.html): {len(product_urls)}")
            
            if product_urls:
                print("  Sample URLs:")
                for purl in product_urls[:5]:
                    print(f"    {purl}")
        except Exception as e:
            print(f"  Error: {e}")

# Try common sitemap patterns
print("\n=== TRYING COMMON SITEMAP PATTERNS ===")
patterns = [
    "/sitemap_index.xml",
    "/sitemap-products.xml",
    "/sitemap-product.xml",
    "/product-sitemap.xml",
    "/sitemap/products.xml",
]

for pattern in patterns:
    url = base_url + pattern
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            print(f"✓ Found: {url}")
            s = BeautifulSoup(resp.text, 'xml')
            locs = s.find_all('loc')
            print(f"  URLs: {len(locs)}")
    except:
        pass
