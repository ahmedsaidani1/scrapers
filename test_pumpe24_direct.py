"""
Test pumpe24 scraper with direct product URLs
"""
from pumpe24_scraper import Pumpe24Scraper


def main():
    print("="*60)
    print("Testing Pumpe24 Scraper - Direct Product Test")
    print("="*60)
    
    scraper = Pumpe24Scraper()
    
    # Test with real product URLs from the site
    test_urls = [
        "https://www.pumpe24.de/pumpe-espa-aspri-15-5m-gg-0-95kw-verkabelt.html",
        "https://www.pumpe24.de/pumpe-ksb-multi-eco-35-p-0-8kw.html",
        "https://www.pumpe24.de/pumpe-pentax-mpx-120-5-1-27kw-ohne-griff-schalter.html",
    ]
    
    print(f"\nTesting {len(test_urls)} products...\n")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{'='*60}")
        print(f"Product {i}: {url}")
        print('='*60)
        
        product = scraper.scrape_product(url)
        
        if product:
            print(f"Name: {product.get('name', 'N/A')}")
            print(f"Manufacturer: {product.get('manufacturer', 'N/A')}")
            print(f"Article #: {product.get('article_number', 'N/A')}")
            print(f"Price (Brutto): {product.get('price_gross', 'N/A')}")
            print(f"Price (Netto): {product.get('price_net', 'N/A')}")
            print(f"Category: {product.get('category', 'N/A')}")
            print(f"EAN: {product.get('ean', 'N/A')}")
        else:
            print("Failed to scrape product")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
