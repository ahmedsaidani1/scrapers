"""
Test a pumpen-heizung.de category page
"""
import requests
from bs4 import BeautifulSoup

test_urls = [
    "https://pumpen-heizung.de/DS-DVS",
    "https://pumpen-heizung.de/Regler-und-Zubehoer",
    "https://pumpen-heizung.de/Hydrojet-Pumpen-MQ-und-JP-Pumpen",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

for url in test_urls:
    print(f"\n{'='*80}")
    print(f"Testing: {url}")
    print('='*80)
    
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for products
    product_selectors = [
        '.product-item',
        '.product',
        'article.product',
        'div.product-box',
        '.item',
        'div[data-product-id]',
    ]
    
    for selector in product_selectors:
        products = soup.select(selector)
        if products:
            print(f"Products with '{selector}': {len(products)}")
    
    # Check for product links
    product_links = soup.select('a[href*="/"]')
    internal_product_links = [
        a.get('href') for a in product_links 
        if a.get('href') and 'pumpen-heizung.de' in a.get('href', '') and a.get('href').count('/') > 2
    ]
    print(f"Potential product links (>2 slashes): {len(set(internal_product_links))}")
    
    # Check for pagination
    pagination_selectors = [
        '.pagination',
        '.pager',
        '.pages',
        'nav.pagination',
        'ul.pagination',
        'div.pagination',
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
                    href = link.get('href', 'N/A')
                    text = link.get_text(strip=True)
                    print(f"    {text}: {href}")
    
    # Check for "next" button
    next_buttons = soup.select('a:contains("weiter"), a:contains("nächste"), a:contains("next"), a.next')
    if next_buttons:
        print(f"Next buttons found: {len(next_buttons)}")
    
    # Save first one
    if url == test_urls[0]:
        with open('pumpenheizung_page_test.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Saved to: pumpenheizung_page_test.html")
