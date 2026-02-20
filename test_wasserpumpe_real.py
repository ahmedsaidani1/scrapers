"""
Test wasserpumpe scraper with real product URLs
"""
from wasserpumpe_scraper import WasserpumpeScraper


def main():
    print("="*60)
    print("Testing Wasserpumpe Scraper - Real Products")
    print("="*60)
    
    scraper = WasserpumpeScraper()
    
    # Use known real product URLs
    product_urls = [
        "https://wasserpumpe.de/dab-divertron-900-m-tauchdruckpumpe",
        "https://wasserpumpe.de/dab-divertron-1200-m-tauchdruckpumpe",
        "https://wasserpumpe.de/grundfos-scala2-3-45-hauswasserwerk",
        "https://wasserpumpe.de/dab-esybox-mini-3-hauswasserwerk",
        "https://wasserpumpe.de/grundfos-jp-5-gartenpumpe",
    ]
    
    print(f"\nTesting {len(product_urls)} known product URLs...")
    
    # Scrape each product
    print("\n2. Scraping product details...")
    products = []
    
    for i, url in enumerate(product_urls, 1):
        print(f"\n   [{i}/{len(product_urls)}] Scraping: {url}")
        product = scraper.scrape_product(url)
        
        if product:
            products.append(product)
            print(f"   ✓ Manufacturer: {product.get('manufacturer', 'N/A')}")
            print(f"   ✓ Name: {product.get('name', 'N/A')[:60]}...")
            print(f"   ✓ Article #: {product.get('article_number', 'N/A')}")
            print(f"   ✓ Price (Gross): {product.get('price_gross', 'N/A')}")
            print(f"   ✓ Price (Net): {product.get('price_net', 'N/A')}")
            print(f"   ✓ EAN: {product.get('ean', 'N/A')}")
            print(f"   ✓ Category: {product.get('category', 'N/A')}")
            print(f"   ✓ Image: {'Yes' if product.get('product_image') else 'No'}")
        else:
            print(f"   ✗ Failed to scrape")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total products scraped: {len(products)}/{len(product_urls)}")
    
    if products:
        print("\nField Coverage:")
        fields = ['manufacturer', 'category', 'name', 'article_number', 
                  'price_gross', 'price_net', 'ean', 'product_image']
        
        for field in fields:
            filled = sum(1 for p in products if p.get(field))
            percentage = (filled / len(products)) * 100
            print(f"  {field:20s}: {filled}/{len(products)} ({percentage:.0f}%)")
        
        print("\nSample Products:")
        for i, sample in enumerate(products[:2], 1):
            print(f"\nProduct {i}:")
            for key, value in sample.items():
                if key in ['name', 'product_image'] and len(str(value)) > 60:
                    print(f"  {key:20s}: {str(value)[:60]}...")
                else:
                    print(f"  {key:20s}: {value}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
