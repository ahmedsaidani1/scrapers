"""
Debug what the scraper actually receives
"""
from wolfonlineshop_scraper import WolfonlineshopScraper

scraper = WolfonlineshopScraper()

# Test the same URLs
test_urls = [
    "https://www.heat-store.de/heizung/fussbodenheizung//",
    "https://www.heat-store.de/heizung/gas-heizung//",
    "https://www.heat-store.de/heizung/heizkoerper//",
]

for url in test_urls:
    print(f"\n{'='*80}")
    print(f"Testing with scraper: {url}")
    print('='*80)
    
    response = scraper.make_request(url)
    if response:
        print(f"Status: {response.status_code}")
        
        soup = scraper.parse_html(response.text)
        
        # Check for products
        products = soup.select('a.product-name')
        print(f"Products found: {len(products)}")
        
        # Check pagination
        pagination = soup.select('li.page-item')
        print(f"Pagination elements: {len(pagination)}")
        
        # Save what scraper sees
        filename = url.split('/')[-3] + '_scraper_view.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved scraper HTML to: {filename}")
    else:
        print("Failed to get response")
