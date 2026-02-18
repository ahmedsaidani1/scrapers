"""
Test the meinhausshop fallback method
"""
import os
import sys

# Set environment variable to test part 1
os.environ['MEINHAUSSHOP_SITEMAP_PARTS'] = '1'

from meinhausshop_scraper import MeinHausShopScraper

def test_fallback():
    """Test the direct sitemap fallback method"""
    
    print("Testing meinhausshop direct sitemap fallback...")
    print(f"MEINHAUSSHOP_SITEMAP_PARTS = {os.getenv('MEINHAUSSHOP_SITEMAP_PARTS')}")
    print()
    
    # Create scraper instance
    scraper = MeinHausShopScraper()
    
    # Test the fallback method directly
    print("Calling _get_urls_from_direct_sitemaps()...")
    product_urls = scraper._get_urls_from_direct_sitemaps()
    
    print()
    print(f"Total product URLs found: {len(product_urls)}")
    print()
    
    if product_urls:
        print("First 10 product URLs:")
        for i, url in enumerate(product_urls[:10], 1):
            print(f"  {i}. {url}")
        print()
        print("✓ Fallback method works!")
    else:
        print("❌ NO PRODUCT URLS FOUND")


if __name__ == "__main__":
    test_fallback()
