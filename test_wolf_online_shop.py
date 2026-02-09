"""
Test script for Wolf-Online-Shop scraper
"""
from wolf_online_shop_scraper import WolfOnlineShopScraper

def test_single_product():
    """Test scraping a single product"""
    print("=" * 60)
    print("Testing Wolf-Online-Shop Scraper - Single Product")
    print("=" * 60)
    
    scraper = WolfOnlineShopScraper()
    
    # Test URL - you can replace with actual product URL
    test_url = "https://www.wolf-online-shop.de"  # Will be replaced with actual product URL
    
    print(f"\nFetching homepage to find a product URL...")
    response = scraper.make_request(test_url)
    
    if response:
        soup = scraper.parse_html(response.text)
        
        # Find first product link
        links = soup.find_all('a', href=True)
        product_url = None
        
        for link in links:
            href = link.get('href')
            if href and ('Art.Nr.' in str(link) or 'product' in href.lower()):
                if href.startswith('/'):
                    product_url = scraper.base_url + href
                elif not href.startswith('http'):
                    product_url = scraper.base_url + '/' + href
                else:
                    product_url = href
                break
        
        if product_url:
            print(f"Testing product: {product_url}")
            product_data = scraper.scrape_product(product_url)
            
            if product_data:
                print("\n✓ Successfully scraped product:")
                print("-" * 60)
                for key, value in product_data.items():
                    print(f"{key:20s}: {value}")
                print("-" * 60)
                return True
            else:
                print("\n✗ Failed to scrape product")
                return False
        else:
            print("\n⚠ Could not find product URL on homepage")
            print("  Try running: python wolf_online_shop_scraper.py")
            return False
    else:
        print("\n✗ Failed to fetch homepage")
        return False

def test_sitemap():
    """Test fetching product URLs from sitemap"""
    print("\n" + "=" * 60)
    print("Testing Sitemap Parsing")
    print("=" * 60)
    
    scraper = WolfOnlineShopScraper()
    
    print("\nFetching product URLs from sitemap (max 10)...")
    product_urls = scraper.get_product_urls(max_urls=10)
    
    if product_urls:
        print(f"\n✓ Found {len(product_urls)} product URLs:")
        for i, url in enumerate(product_urls[:5], 1):
            print(f"  {i}. {url}")
        if len(product_urls) > 5:
            print(f"  ... and {len(product_urls) - 5} more")
        return True
    else:
        print("\n✗ No product URLs found")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("WOLF-ONLINE-SHOP SCRAPER TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Sitemap
    results.append(("Sitemap Parsing", test_sitemap()))
    
    # Test 2: Single product
    results.append(("Single Product", test_single_product()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Scraper is ready to use.")
        print("\nRun the full scraper with:")
        print("  python wolf_online_shop_scraper.py")
        print("\nOr scrape limited products:")
        print("  python run_wolf_online_shop_50.py")
    else:
        print("\n⚠ Some tests failed. Check errors above.")

if __name__ == "__main__":
    main()
