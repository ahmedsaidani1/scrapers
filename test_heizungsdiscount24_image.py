"""
Test heizungsdiscount24 image extraction
"""
from heizungsdiscount24_scraper import Heizungsdiscount24Scraper

def test_image_extraction():
    scraper = Heizungsdiscount24Scraper()
    
    # Get first 5 product URLs
    print("Getting product URLs...")
    urls = scraper.get_product_urls()
    
    if not urls:
        print("No URLs found!")
        return
    
    print(f"\nTesting first 5 products from {len(urls)} total URLs\n")
    
    # Test first 5 products
    for i, url in enumerate(urls[:5], 1):
        print(f"\n[{i}/5] Testing: {url}")
        product = scraper.scrape_product(url)
        
        if product:
            print(f"  Name: {product.get('name', 'N/A')[:60]}")
            print(f"  Manufacturer: {product.get('manufacturer', 'N/A')}")
            print(f"  Price: {product.get('price_gross', 'N/A')}")
            print(f"  EAN: {product.get('ean', 'N/A')}")
            print(f"  Image: {product.get('product_image', 'N/A')[:80]}")
            
            if not product.get('product_image'):
                print("  ⚠ IMAGE MISSING!")
        else:
            print("  ✗ Failed to scrape")

if __name__ == "__main__":
    test_image_extraction()
