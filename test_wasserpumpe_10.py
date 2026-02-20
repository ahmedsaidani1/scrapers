"""
Test wasserpumpe scraper with 10 products from first category only
"""
from wasserpumpe_scraper import WasserpumpeScraper


def main():
    print("="*60)
    print("Testing Wasserpumpe Scraper - 10 Products from Sitemap")
    print("="*60)
    
    scraper = WasserpumpeScraper()
    
    # Get product URLs from sitemap (more reliable than category pages)
    print("\n1. Getting product URLs from sitemap...")
    product_urls = scraper._extract_urls_from_sitemap(max_urls=10)
    
    print(f"   Found {len(product_urls)} product URLs")
    
    if not product_urls:
        print("\n❌ No products found!")
        return
    
    # Scrape each product
    print("\n2. Scraping product details...")
    products = []
    
    for i, url in enumerate(product_urls, 1):
        print(f"\n   [{i}/10] Scraping: {url}")
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
    print(f"Total products scraped: {len(products)}/10")
    
    if products:
        print("\nField Coverage:")
        fields = ['manufacturer', 'category', 'name', 'article_number', 
                  'price_gross', 'price_net', 'ean', 'product_image']
        
        for field in fields:
            filled = sum(1 for p in products if p.get(field))
            percentage = (filled / len(products)) * 100
            print(f"  {field:20s}: {filled}/{len(products)} ({percentage:.0f}%)")
        
        print("\nSample Product:")
        sample = products[0]
        for key, value in sample.items():
            if key == 'name' and len(str(value)) > 60:
                print(f"  {key:20s}: {str(value)[:60]}...")
            elif key == 'product_image' and len(str(value)) > 60:
                print(f"  {key:20s}: {str(value)[:60]}...")
            else:
                print(f"  {key:20s}: {value}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
