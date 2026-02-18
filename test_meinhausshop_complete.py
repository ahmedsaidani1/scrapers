"""
Test the complete meinhausshop flow with both methods
"""
import os
import sys

# Set environment variable to test part 1
os.environ['MEINHAUSSHOP_SITEMAP_PARTS'] = '1'

from meinhausshop_scraper import MeinHausShopScraper

def test_complete():
    """Test the complete flow"""
    
    print("Testing meinhausshop complete flow...")
    print(f"MEINHAUSSHOP_SITEMAP_PARTS = {os.getenv('MEINHAUSSHOP_SITEMAP_PARTS')}")
    print()
    
    # Create scraper instance
    scraper = MeinHausShopScraper()
    
    # Test the normal method (should work locally)
    print("=" * 80)
    print("TEST 1: Normal method (via main sitemap)")
    print("=" * 80)
    product_urls = scraper.get_product_urls()
    
    print()
    print(f"Result: {len(product_urls)} product URLs found")
    print()
    
    if product_urls:
        print("First 5 URLs:")
        for i, url in enumerate(product_urls[:5], 1):
            print(f"  {i}. {url}")
        print()
        print("SUCCESS: Normal method works!")
    else:
        print("FAILED: No URLs found with normal method")
    
    print()
    print("=" * 80)
    print("TEST 2: Fallback method (direct sitemaps)")
    print("=" * 80)
    
    # Test the fallback method
    fallback_urls = scraper._get_urls_from_direct_sitemaps()
    
    print()
    print(f"Result: {len(fallback_urls)} product URLs found")
    print()
    
    if fallback_urls:
        print("First 5 URLs:")
        for i, url in enumerate(fallback_urls[:5], 1):
            print(f"  {i}. {url}")
        print()
        print("SUCCESS: Fallback method works!")
    else:
        print("FAILED: No URLs found with fallback method")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Normal method:   {len(product_urls):,} URLs")
    print(f"Fallback method: {len(fallback_urls):,} URLs")
    print()
    
    if product_urls and fallback_urls:
        print("Both methods work! The scraper is resilient.")
    elif fallback_urls:
        print("Only fallback works - but that's OK, it will be used on Render!")
    else:
        print("ERROR: Neither method works")


if __name__ == "__main__":
    test_complete()
