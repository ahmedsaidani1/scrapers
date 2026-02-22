"""
Debug Nuxt.js API routes for Selfio
"""
import requests
import json
import re

url = "https://www.selfio.de/produkte/ideal-standard-brausethermostat-ap-cerat-ausld-80mm-chrom"
product_slug = "ideal-standard-brausethermostat-ap-cerat-ausld-80mm-chrom"

print("Testing Nuxt.js API patterns...\n")

# Common Nuxt.js API patterns
api_patterns = [
    f"https://www.selfio.de/_nuxt/data/product/{product_slug}.json",
    f"https://www.selfio.de/api/product/{product_slug}",
    f"https://www.selfio.de/api/products/{product_slug}",
    f"https://www.selfio.de/_nuxt/payload.json",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

for api_url in api_patterns:
    print(f"Testing: {api_url}")
    try:
        r = requests.get(api_url, headers=headers, timeout=5)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            print(f"  ✓ SUCCESS!")
            try:
                data = r.json()
                print(f"  Keys: {list(data.keys())[:10]}")
                # Look for productNumber
                json_str = json.dumps(data)
                if 'productNumber' in json_str:
                    print(f"  ✓✓ Contains productNumber!")
                    # Try to extract it
                    matches = re.findall(r'"productNumber"\s*:\s*"([^"]+)"', json_str)
                    if matches:
                        print(f"  Article numbers found: {matches[:5]}")
                print(f"\n  Sample data: {json_str[:500]}\n")
            except:
                print(f"  Response (first 500 chars): {r.text[:500]}")
        elif r.status_code == 404:
            print(f"  Not found")
        else:
            print(f"  Response: {r.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()

# Try to extract from the main page's __NUXT__ data more carefully
print("\n" + "="*60)
print("Analyzing __NUXT__ state in detail...")
print("="*60 + "\n")

r = requests.get(url, headers=headers)
html = r.text

# Look for window.__NUXT__
if 'window.__NUXT__' in html:
    print("Found window.__NUXT__ assignment")
    
    # Extract the __NUXT__ object
    match = re.search(r'window\.__NUXT__\s*=\s*(.+?);\s*</script>', html, re.DOTALL)
    if match:
        nuxt_data = match.group(1)
        print(f"__NUXT__ data length: {len(nuxt_data)} characters")
        
        # Look for productNumber in the data
        if 'productNumber' in nuxt_data:
            print("\n✓ Found 'productNumber' in __NUXT__ data!")
            
            # Try to extract it with regex
            # Pattern 1: "productNumber":"VALUE"
            matches = re.findall(r'"productNumber"\s*:\s*"([^"]+)"', nuxt_data)
            if matches:
                print(f"  Pattern 1 matches: {matches}")
            
            # Pattern 2: productNumber:"VALUE"
            matches = re.findall(r'productNumber\s*:\s*"([^"]+)"', nuxt_data)
            if matches:
                print(f"  Pattern 2 matches: {matches}")
            
            # Show context around productNumber
            idx = nuxt_data.find('productNumber')
            if idx != -1:
                context = nuxt_data[max(0, idx-100):min(len(nuxt_data), idx+200)]
                print(f"\n  Context around productNumber:")
                print(f"  {context}")
        else:
            print("  'productNumber' not found in __NUXT__ data")
            
            # Check for other product-related fields
            product_fields = ['sku', 'articleNumber', 'itemNumber', 'article', 'nummer']
            for field in product_fields:
                if field in nuxt_data.lower():
                    print(f"  Found '{field}' in data")

print("\n" + "="*60)
print("Analysis complete!")
