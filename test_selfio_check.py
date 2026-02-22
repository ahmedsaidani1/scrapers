"""
Test selfio manufacturer, article number, and price extraction
"""
from selfio_scraper import SelfioScraper

def test_selfio():
    scraper = SelfioScraper()
    
    # Get first 20 products
    print("Getting product URLs...")
    all_urls = scraper.get_product_urls()
    urls = all_urls[:20] if len(all_urls) > 20 else all_urls
    
    if not urls:
        print("No URLs found!")
        return
    
    print(f"\nTesting {len(urls)} products\n")
    
    manufacturer_count = 0
    article_count = 0
    price_count = 0
    ean_count = 0
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        product = scraper.scrape_product(url)
        
        if product:
            print(f"  Name: {product.get('name', 'N/A')[:60]}")
            print(f"  Manufacturer: {product.get('manufacturer', 'N/A')}")
            print(f"  Article: {product.get('article_number', 'N/A')}")
            print(f"  Price: {product.get('price_gross', 'N/A')}")
            print(f"  EAN: {product.get('ean', 'N/A')}")
            
            if product.get('manufacturer'):
                manufacturer_count += 1
            else:
                print("  ! MANUFACTURER MISSING!")
                
            if product.get('article_number'):
                article_count += 1
            else:
                print("  ! ARTICLE NUMBER MISSING!")
                
            if product.get('price_gross'):
                price_count += 1
            else:
                print("  ! PRICE MISSING!")
                
            if product.get('ean'):
                ean_count += 1
            else:
                print("  ! EAN MISSING!")
        else:
            print("  ✗ Failed")
        print()
    
    print(f"\nResults:")
    print(f"  Manufacturer: {manufacturer_count}/{len(urls)} ({manufacturer_count*100//len(urls) if len(urls) > 0 else 0}%)")
    print(f"  Article Number: {article_count}/{len(urls)} ({article_count*100//len(urls) if len(urls) > 0 else 0}%)")
    print(f"  Price: {price_count}/{len(urls)} ({price_count*100//len(urls) if len(urls) > 0 else 0}%)")
    print(f"  EAN: {ean_count}/{len(urls)} ({ean_count*100//len(urls) if len(urls) > 0 else 0}%)")

if __name__ == "__main__":
    test_selfio()
