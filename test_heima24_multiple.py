"""
Test script to verify EAN extraction for multiple heima24.de products
"""
from heima24_scraper import Heima24Scraper


def test_multiple_products():
    """Test EAN extraction from multiple products."""
    scraper = Heima24Scraper()
    
    # Test multiple product URLs
    test_urls = [
        "https://www.heima24.de/rohrsysteme/mehrschichtverbundrohr-16-x-2-mm-rolle-mit-25-m-dvgw-geprueft.html",
        "https://www.heima24.de/rohrsysteme/mehrschichtverbundrohr-16-x-2-mm-rolle-mit-50-m-dvgw-geprueft.html",
        "https://www.heima24.de/rohrsysteme/mehrschichtverbundrohr-16-x-2-mm-rolle-mit-100-m-dvgw-geprueft.html",
    ]
    
    print(f"Testing EAN extraction from {len(test_urls)} products\n")
    print("="*80)
    
    success_count = 0
    ean_count = 0
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}] Testing: {url.split('/')[-1][:60]}...")
        
        product_data = scraper.scrape_product(url)
        
        if product_data:
            success_count += 1
            name = product_data.get('name', 'N/A')
            ean = product_data.get('ean', '')
            article_num = product_data.get('article_number', 'N/A')
            manufacturer = product_data.get('manufacturer', 'N/A')
            
            print(f"  ✓ Name: {name[:60]}")
            print(f"  ✓ Manufacturer: {manufacturer}")
            print(f"  ✓ Article: {article_num}")
            
            if ean:
                ean_count += 1
                print(f"  ✓ EAN: {ean}")
            else:
                print(f"  ✗ EAN: Not found")
        else:
            print(f"  ✗ Failed to scrape")
    
    print("\n" + "="*80)
    print(f"\nResults:")
    print(f"  Products scraped: {success_count}/{len(test_urls)}")
    print(f"  EANs extracted: {ean_count}/{len(test_urls)}")
    
    if ean_count == len(test_urls):
        print(f"\n✓ SUCCESS: All products have EAN extracted!")
    else:
        print(f"\n⚠ WARNING: {len(test_urls) - ean_count} products missing EAN")


if __name__ == "__main__":
    test_multiple_products()
