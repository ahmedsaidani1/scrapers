"""
Debug script to find Selfio API endpoints for product data
"""
import requests
import json
import re
from bs4 import BeautifulSoup

# Test product URL
url = "https://www.selfio.de/produkte/ideal-standard-brausethermostat-ap-cerat-ausld-80mm-chrom"

print("Analyzing Selfio for API endpoints...\n")

# Get the page
response = requests.get(url)
html = response.text

print("1. Checking for API endpoints in HTML...")
# Look for API URLs in the HTML
api_patterns = [
    r'https://[^"\']+/api/[^"\']+',
    r'https://[^"\']+/store-api/[^"\']+',
    r'/api/[^"\']+',
    r'/store-api/[^"\']+',
]

found_apis = set()
for pattern in api_patterns:
    matches = re.findall(pattern, html)
    found_apis.update(matches)

if found_apis:
    print(f"  Found {len(found_apis)} potential API endpoints:")
    for api in list(found_apis)[:10]:
        print(f"    {api}")
else:
    print("  No API endpoints found in HTML")

# Check for product ID in URL or HTML
print("\n2. Extracting product identifier...")
# Try to find product ID from URL
url_parts = url.split('/')
product_slug = url_parts[-1] if url_parts else ""
print(f"  Product slug: {product_slug}")

# Look for product ID in HTML
soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')

product_id = None
for script in scripts:
    if script.string and 'productId' in script.string:
        # Try to extract product ID
        match = re.search(r'productId["\']?\s*:\s*["\']([^"\']+)', script.string)
        if match:
            product_id = match.group(1)
            print(f"  Found productId: {product_id}")
            break

# Check for Shopware store-api
print("\n3. Testing Shopware 6 store-api endpoints...")
base_url = "https://www.selfio.de"

# Common Shopware 6 API endpoints
api_endpoints = [
    f"{base_url}/store-api/product/{product_id}" if product_id else None,
    f"{base_url}/store-api/product",
    f"{base_url}/api/product/{product_id}" if product_id else None,
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'sw-access-key': 'SWSCBHFSNTVMAWNZDNFKSHLAYW',  # Common default
}

for endpoint in api_endpoints:
    if not endpoint:
        continue
    
    print(f"\n  Testing: {endpoint}")
    try:
        r = requests.get(endpoint, headers=headers, timeout=5)
        print(f"    Status: {r.status_code}")
        if r.status_code == 200:
            try:
                data = r.json()
                print(f"    Response keys: {list(data.keys())[:10]}")
                if 'productNumber' in str(data):
                    print(f"    ✓ Contains productNumber!")
            except:
                print(f"    Response length: {len(r.text)}")
    except Exception as e:
        print(f"    Error: {e}")

# Check for GraphQL endpoint
print("\n4. Checking for GraphQL endpoint...")
graphql_url = f"{base_url}/graphql"
try:
    r = requests.post(graphql_url, json={'query': '{__schema{types{name}}}'}, timeout=5)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        print("  ✓ GraphQL endpoint found!")
except Exception as e:
    print(f"  No GraphQL: {e}")

# Look for __NUXT__ data with product info
print("\n5. Analyzing __NUXT__ state data...")
if '__NUXT__' in html:
    print("  Found __NUXT__ data")
    # Try to extract the state
    match = re.search(r'window\.__NUXT__\s*=\s*({.+?});?\s*</script>', html, re.DOTALL)
    if match:
        print("  Attempting to parse __NUXT__ state...")
        try:
            # This is tricky because it's JavaScript, not JSON
            print("  __NUXT__ data found but requires JavaScript parsing")
            print("  Checking for productNumber in raw data...")
            if 'productNumber' in html:
                # Find all occurrences
                matches = re.findall(r'productNumber["\']?\s*:\s*["\']([^"\']+)', html)
                if matches:
                    print(f"  Found productNumber values: {matches[:5]}")
        except Exception as e:
            print(f"  Error parsing: {e}")

print("\n6. Checking for alternative data sources...")
# Check meta tags
for meta in soup.find_all('meta'):
    if meta.get('property') or meta.get('name'):
        prop = meta.get('property') or meta.get('name')
        if 'product' in prop.lower():
            print(f"  Meta: {prop} = {meta.get('content', 'N/A')[:80]}")

print("\n" + "="*60)
print("Analysis complete!")
