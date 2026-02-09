"""
Test script for MeinHausShop scraper - tests a few products only
"""
from meinhausshop_scraper import MeinHausShopScraper

def test_single_product():
    """Test scraping a single product."""
    scraper = MeinHausShopScraper()
    
    # Test URL
    test_url = "https://www.meinhausshop.de/Verschraubungssatz-1-1-4-fuer-Umwaelzpumpen"
    
    print(f"Testing product: {test_url}")
    print("="*60)
    
    product_data = scraper.scrape_product(test_url)
    
    if product_data:
        print("\n✓ Successfully scraped product:")
        for key, value in product_data.items():
            print(f"  {key}: {value}")
    else:
        print("\n✗ Failed to scrape product")
    
    return product_data is not None


def test_sitemap():
    """Test getting product URLs from sitemap."""
    scraper = MeinHausShopScraper()
    
    print("Testing sitemap parsing...")
    print("="*60)
    
    # Get first 10 URLs only for testing
    urls = scraper.get_product_urls()
    
    print(f"\n✓ Found {len(urls)} total product URLs")
    print("\nFirst 10 URLs:")
    for i, url in enumerate(urls[:10], 1):
        print(f"  {i}. {url}")
    
    return len(urls) > 0


if __name__ == "__main__":
    print("MeinHausShop Scraper Test")
    print("="*60)
    
    # Test 1: Single product
    print("\n\nTEST 1: Single Product Scraping")
    test1_passed = test_single_product()
    
    # Test 2: Sitemap
    print("\n\nTEST 2: Sitemap Parsing")
    test2_passed = test_sitemap()
    
    # Summary
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Single Product Test: {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Sitemap Test: {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    print("="*60)
