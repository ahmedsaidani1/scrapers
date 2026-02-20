"""
Test category extraction from URL for wasserpumpe scraper
Only scrapes first 2 categories to verify the approach works
"""
import sys
sys.path.insert(0, '.')

from wasserpumpe_scraper import WasserpumpeScraper

def test_category_extraction():
    """Test category extraction from URLs with limited categories"""
    
    scraper = WasserpumpeScraper()
    
    # Override to use only first 2 categories for quick testing
    scraper.category_urls = scraper.category_urls[:2]
    
    print(f"\n{'='*60}")
    print(f"Testing category extraction with {len(scraper.category_urls)} categories")
    print(f"{'='*60}\n")
    
    for cat_url in scraper.category_urls:
        print(f"Category URL: {cat_url}")
        category_name = scraper._parse_category_from_url(cat_url)
        print(f"Extracted Category: {category_name}\n")
    
    # Get product URLs directly from categories (skip sitemap)
    print("\nFetching product URLs from categories (max 10)...")
    product_urls = scraper._extract_urls_from_categories(max_urls=10)
    
    print(f"\nFound {len(product_urls)} product URLs")
    
    if not product_urls:
        print("No products found!")
        return
    
    # Test scraping first 3 products
    print(f"\n{'='*60}")
    print("Testing product scraping with category extraction")
    print(f"{'='*60}\n")
    
    for i, url in enumerate(product_urls[:3], 1):
        print(f"\n[{i}/3] Scraping: {url}")
        product = scraper.scrape_product(url)
        
        if product:
            print(f"  Name: {product['name'][:50]}...")
            print(f"  Manufacturer: {product['manufacturer']}")
            print(f"  Category: {product['category']}")
            print(f"  Price: {product['price_gross']}")
            print(f"  Article #: {product['article_number']}")
        else:
            print("  Failed to scrape product")
    
    print(f"\n{'='*60}")
    print("Test complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_category_extraction()
