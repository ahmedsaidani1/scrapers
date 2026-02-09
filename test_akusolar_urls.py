"""Test to find actual Akusolar product URLs"""
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()

r = requests.get('https://akusolar.fcostry3.cz/', verify=False)
soup = BeautifulSoup(r.text, 'html.parser')

print("=== Looking for product links ===\n")

links = soup.find_all('a', href=True)
product_links = [a for a in links if 'rozvodnicova' in a.get('href', '').lower()]

print(f"Found {len(product_links)} product links:\n")

for a in product_links:
    text = a.text.strip()[:60]
    url = a.get('href')
    print(f"Text: {text}")
    print(f"URL: {url}")
    print()

# Test if URLs work
print("\n=== Testing URLs ===\n")
for a in product_links:
    url = a.get('href')
    if url.startswith('/'):
        full_url = 'https://akusolar.fcostry3.cz' + url
    else:
        full_url = url
    
    try:
        test_r = requests.get(full_url, verify=False, timeout=5)
        print(f"{full_url}: {test_r.status_code}")
    except Exception as e:
        print(f"{full_url}: ERROR - {e}")
