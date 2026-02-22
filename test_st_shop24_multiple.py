"""
Test st_shop24 with multiple products
"""
from st_shop24_scraper import StShop24Scraper

def test_multiple_products():
    scraper = StShop24Scraper()
    
    # Get first 10 products
    print("Getting product URLs...")
    urls = scraper.get_product_urls(max_urls=10)
    
    if not urls:
        print("No URLs found!")
        return
    
    print(f"\nTesting {len(urls)} products\n")
    
    ean_count = 0
    article_count = 0
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        product = scraper.scrape_product(url)
        
        if product:
            print(f"  Name: {product.get('name', 'N/A')[:60]}")
            print(f"  Manufacturer: {product.get('manufacturer', 'N/A')}")
            print(f"  Article: {product.get('article_number', 'N/A')}")
            print(f"  EAN: {product.get('ean', 'N/A')}")
            print(f"  Price: {product.get('price_gross', 'N/A')}")
            
            if product.get('ean'):
                ean_count += 1
            if product.get('article_number'):
                article_count += 1
        else:
            print("  ✗ Failed")
        print()
    
    print(f"\nResults:")
    print(f"  EAN: {ean_count}/{len(urls)} ({ean_count*100//len(urls)}%)")
    print(f"  Article Number: {article_count}/{len(urls)} ({article_count*100//len(urls)}%)")

if __name__ == "__main__":
    test_multiple_products()
