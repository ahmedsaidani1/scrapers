"""
Test if subcategory products are included in parent category
"""
from wolfonlineshop_scraper import WolfonlineshopScraper
import time

scraper = WolfonlineshopScraper()

# Test parent and child categories
test_cases = [
    {
        'parent': 'https://www.heat-store.de/heizung//',
        'children': [
            'https://www.heat-store.de/heizung/fussbodenheizung//',
            'https://www.heat-store.de/heizung/gas-heizung//',
        ]
    }
]

for case in test_cases:
    print(f"\n{'='*80}")
    print(f"Parent: {case['parent']}")
    print('='*80)
    
    # Get products from parent
    parent_response = scraper.make_request(case['parent'])
    if parent_response:
        parent_soup = scraper.parse_html(parent_response.text)
        parent_products = parent_soup.select('a.product-name')
        parent_urls = set([p.get('href', '') for p in parent_products])
        print(f"Parent has {len(parent_urls)} products on page 1")
        
        # Sample some URLs
        for url in list(parent_urls)[:3]:
            print(f"  - {url}")
    
    time.sleep(1)
    
    # Check children
    for child_url in case['children']:
        print(f"\nChild: {child_url}")
        child_response = scraper.make_request(child_url)
        if child_response:
            child_soup = scraper.parse_html(child_response.text)
            child_products = child_soup.select('a.product-name')
            child_urls = set([p.get('href', '') for p in child_products])
            print(f"  Child has {len(child_urls)} products on page 1")
            
            # Sample some URLs
            for url in list(child_urls)[:3]:
                print(f"    - {url}")
            
            # Check overlap
            if parent_response:
                overlap = parent_urls & child_urls
                print(f"  Overlap with parent: {len(overlap)} products")
        
        time.sleep(1)
