"""
Debug script to test meinhausshop sitemap parts filtering
"""
import os
import sys

# Set environment variable to test
os.environ['MEINHAUSSHOP_SITEMAP_PARTS'] = '2'

# Import the scraper
from meinhausshop_scraper import MeinHausShopScraper

def test_sitemap_parts():
    """Test the sitemap parts filtering logic"""
    
    print("Testing meinhausshop sitemap parts filtering...")
    print(f"MEINHAUSSHOP_SITEMAP_PARTS = {os.getenv('MEINHAUSSHOP_SITEMAP_PARTS')}")
    print()
    
    # Create scraper instance
    scraper = MeinHausShopScraper()
    
    # Get product URLs (this will use the filtering logic)
    print("Calling get_product_urls()...")
    product_urls = scraper.get_product_urls()
    
    print()
    print(f"Total product URLs found: {len(product_urls)}")
    print()
    
    if product_urls:
        print("First 10 product URLs:")
        for i, url in enumerate(product_urls[:10], 1):
            print(f"  {i}. {url}")
    else:
        print("❌ NO PRODUCT URLS FOUND - This is the problem!")
        print()
        print("This means the sitemap part filtering is not working correctly.")


if __name__ == "__main__":
    test_sitemap_parts()
