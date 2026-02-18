"""
Test if pumpenheizung scraper extracts prices correctly
"""
from pumpenheizung_scraper import PumpenheizungScraper

scraper = PumpenheizungScraper()

# Test with a few product URLs
test_urls = [
    "https://pumpen-heizung.de/Unterwassermotorpumpe_s1",
    "https://pumpen-heizung.de/KSB-01116438-Zub-Abgangsstueck-Flansch",
]

print("Testing price extraction...\n")

for url in test_urls:
    print(f"{'='*80}")
    print(f"URL: {url}")
    print('='*80)
    
    product_data = scraper.scrape_product(url)
    
    if product_data:
        print(f"Name: {product_data.get('name', 'N/A')}")
        print(f"Manufacturer: {product_data.get('manufacturer', 'N/A')}")
        print(f"Price Gross: {product_data.get('price_gross', 'N/A')}")
        print(f"Price Net: {product_data.get('price_net', 'N/A')}")
        print(f"Article Number: {product_data.get('article_number', 'N/A')}")
        print(f"EAN: {product_data.get('ean', 'N/A')}")
        print(f"Category: {product_data.get('category', 'N/A')}")
    else:
        print("Failed to scrape product")
    
    print()
