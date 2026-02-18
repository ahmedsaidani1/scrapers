"""
Debug pumpen-heizung.de structure
"""
import requests
from bs4 import BeautifulSoup

base_url = "https://pumpen-heizung.de"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Check sitemap
print("Checking sitemap...")
sitemap_url = f"{base_url}/sitemap.xml"
response = requests.get(sitemap_url, headers=headers, timeout=30)
print(f"Sitemap status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'xml')
locs = soup.find_all('loc')
print(f"Total URLs in sitemap: {len(locs)}")

# Categorize URLs
categories = []
products = []
sitemaps = []

for loc in locs:
    url = loc.text.strip()
    if 'sitemap' in url.lower() or url.endswith('.xml'):
        sitemaps.append(url)
    elif url.count('/') <= 4 and not url.split('/')[-1].count('-') > 3:
        categories.append(url)
    else:
        products.append(url)

print(f"Sub-sitemaps: {len(sitemaps)}")
print(f"Potential categories: {len(categories)}")
print(f"Potential products: {len(products)}\n")

if sitemaps:
    print("First 5 sub-sitemaps:")
    for url in sitemaps[:5]:
        print(f"  {url}")

if categories:
    print("\nFirst 10 category URLs:")
    for url in categories[:10]:
        print(f"  {url}")
        
    # Test a category page
    test_cat = categories[0] if categories else None
    if test_cat:
        print(f"\n{'='*80}")
        print(f"Testing category: {test_cat}")
        print('='*80)
        
        response = requests.get(test_cat, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for products
        product_selectors = [
            '.product-item',
            '.product',
            'article.product',
            'div.product-box',
        ]
        
        for selector in product_selectors:
            products_found = soup.select(selector)
            if products_found:
                print(f"Products with '{selector}': {len(products_found)}")
        
        # Check pagination
        pagination_selectors = [
            '.pagination',
            '.pager',
            '.pages',
            'nav.pagination',
        ]
        
        for selector in pagination_selectors:
            pag = soup.select(selector)
            if pag:
                print(f"Pagination with '{selector}': {len(pag)}")
                
                # Check for page links
                page_links = soup.select(f'{selector} a')
                if page_links:
                    print(f"  Page links: {len(page_links)}")
                    print(f"  Sample links:")
                    for link in page_links[:5]:
                        print(f"    {link.get('href', 'N/A')}")
        
        # Save HTML
        with open('pumpenheizung_category_test.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Saved to: pumpenheizung_category_test.html")
