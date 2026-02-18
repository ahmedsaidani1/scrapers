"""
Analyze URL patterns on heat-store.de
"""
import requests
from bs4 import BeautifulSoup

url = "https://www.heat-store.de/heizung/heizkoerper/badheizkoerper//"
response = requests.get(url, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

print("=== ANALYZING URL PATTERNS ===\n")

# Get product-name links (these are the actual products)
product_links = soup.select('a.product-name')
print(f"Found {len(product_links)} product-name links:\n")

for i, link in enumerate(product_links[:10], 1):
    href = link.get('href', '')
    text = link.get_text(strip=True)[:60]
    
    # Analyze the URL
    has_double_slash = '//' in href
    ends_with_html = href.endswith('.html')
    has_detail = '/detail/' in href
    
    print(f"{i}. {text}")
    print(f"   URL: {href}")
    print(f"   Has //: {has_double_slash}, Ends .html: {ends_with_html}, Has /detail/: {has_detail}")
    print()

# Check if there are category links too
print("\n=== CATEGORY LINKS (should have //) ===\n")
all_links = soup.find_all('a', href=True)
category_links = [link for link in all_links if '//' in link.get('href', '') and link.get('href', '').startswith('/')]
print(f"Found {len(category_links)} category links")
for i, link in enumerate(category_links[:5], 1):
    href = link.get('href', '')
    text = link.get_text(strip=True)[:60]
    print(f"{i}. {text} -> {href}")
