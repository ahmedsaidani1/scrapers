"""
Test script to verify EAN extraction for heima24.de
"""
from heima24_scraper import Heima24Scraper


def test_ean_extraction():
    """Test EAN extraction from a sample product."""
    scraper = Heima24Scraper()
    
    # Test product URL (from sitemap)
    test_url = "https://www.heima24.de/rohrsysteme/mehrschichtverbundrohr-16-x-2-mm-rolle-mit-25-m-dvgw-geprueft.html"
    
    print(f"Testing EAN extraction from: {test_url}\n")
    
    product_data = scraper.scrape_product(test_url)
    
    if product_data:
        print("✓ Product scraped successfully!")
        print(f"\nProduct Details:")
        print(f"  Name: {product_data.get('name', 'N/A')}")
        print(f"  Manufacturer: {product_data.get('manufacturer', 'N/A')}")
        print(f"  Article Number: {product_data.get('article_number', 'N/A')}")
        print(f"  EAN: {product_data.get('ean', 'N/A')}")
        print(f"  Price Gross: {product_data.get('price_gross', 'N/A')}")
        print(f"  Price Net: {product_data.get('price_net', 'N/A')}")
        print(f"  Category: {product_data.get('category', 'N/A')}")
        print(f"  Image: {product_data.get('product_image', 'N/A')[:80]}...")
        
        # Verify EAN is extracted
        if product_data.get('ean'):
            print(f"\n✓ SUCCESS: EAN extracted: {product_data['ean']}")
            print(f"  Expected EAN: 4059915033739")
            if product_data['ean'] == '4059915033739':
                print(f"  ✓ EAN matches expected value!")
            else:
                print(f"  ✗ EAN does not match expected value")
        else:
            print(f"\n✗ FAILED: EAN not extracted")
    else:
        print("✗ Failed to scrape product")


if __name__ == "__main__":
    test_ean_extraction()
