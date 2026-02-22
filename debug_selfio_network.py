"""
Try to find the API endpoint by analyzing common patterns
"""
import requests
import json
import re

# Get the product page
url = "https://www.selfio.de/produkte/ideal-standard-brausethermostat-ap-cerat-ausld-80mm-chrom"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

print("Fetching product page...")
r = requests.get(url, headers=headers)
html = r.text

print("\nLooking for API configuration...")

# Look for API base URL in the HTML
api_patterns = [
    r'"apiUrl"\s*:\s*"([^"]+)"',
    r'"baseUrl"\s*:\s*"([^"]+)"',
    r'"endpoint"\s*:\s*"([^"]+)"',
    r'API_URL\s*=\s*"([^"]+)"',
]

for pattern in api_patterns:
    matches = re.findall(pattern, html)
    if matches:
        print(f"  Found API URL: {matches[0]}")

# Extract product ID from URL or page
print("\nExtracting product identifier...")

# Method 1: From URL path
url_slug = url.split('/')[-1]
print(f"  URL slug: {url_slug}")

# Method 2: Look for product ID in scripts
product_id_patterns = [
    r'"id"\s*:\s*"([a-f0-9]{32})"',  # UUID format
    r'"productId"\s*:\s*"([^"]+)"',
    r'data-product-id="([^"]+)"',
]

for pattern in product_id_patterns:
    matches = re.findall(pattern, html)
    if matches:
        print(f"  Found product ID: {matches[0]}")
        product_id = matches[0]
        break

# Try Shopware 6 context endpoint
print("\nTrying Shopware 6 context endpoint...")
context_url = "https://www.selfio.de/store-api/context"
try:
    r = requests.get(context_url, headers=headers)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Keys: {list(data.keys())}")
        if 'token' in data:
            print(f"  ✓ Got context token: {data['token'][:20]}...")
except Exception as e:
    print(f"  Error: {e}")

# Try to find the actual API endpoint by looking at script sources
print("\nAnalyzing script sources...")
soup_scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
print(f"  Found {len(soup_scripts)} script sources")

# Look for _nuxt scripts that might contain the API logic
nuxt_scripts = [s for s in soup_scripts if '_nuxt' in s]
print(f"  Nuxt scripts: {len(nuxt_scripts)}")
if nuxt_scripts:
    print(f"  Sample: {nuxt_scripts[0]}")

# Check if there's a Shopware sales channel access key
print("\nLooking for Shopware access key...")
access_key_patterns = [
    r'"sw-access-key"\s*:\s*"([^"]+)"',
    r'sw-access-key:\s*"([^"]+)"',
    r'accessKey:\s*"([^"]+)"',
]

for pattern in access_key_patterns:
    matches = re.findall(pattern, html)
    if matches:
        print(f"  Found access key: {matches[0]}")
        access_key = matches[0]
        
        # Try using it
        print(f"\n  Testing with access key...")
        test_headers = headers.copy()
        test_headers['sw-access-key'] = access_key
        
        test_url = "https://www.selfio.de/store-api/product"
        try:
            r = requests.post(test_url, headers=test_headers, json={})
            print(f"    Status: {r.status_code}")
            if r.status_code == 200:
                print(f"    ✓ API works!")
        except Exception as e:
            print(f"    Error: {e}")

# Final attempt: Check for data in inline scripts
print("\nChecking inline scripts for product data...")
inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"  Found {len(inline_scripts)} inline scripts")

for i, script in enumerate(inline_scripts):
    if 'productNumber' in script or 'article' in script.lower():
        print(f"\n  Script {i} contains product data:")
        print(f"    Length: {len(script)} chars")
        if 'productNumber' in script:
            # Try to extract
            matches = re.findall(r'productNumber["\']?\s*:\s*["\']([^"\']+)', script)
            if matches:
                print(f"    ✓ Found productNumber: {matches}")

print("\n" + "="*60)
print("Analysis complete!")
