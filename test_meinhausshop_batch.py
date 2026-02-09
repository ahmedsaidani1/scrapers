"""
Test batch scraping for MeinHausShop - scrapes first 5 products only
"""
from meinhausshop_scraper import MeinHausShopScraper
import csv

def test_batch_scraping():
    """Test scraping first 5 products."""
    scraper = MeinHausShopScraper()
    
    print("Getting product URLs...")
    all_urls = scraper.get_product_urls()
    
    # Take only first 5 for testing
    test_urls = all_urls[:5]
    
    print(f"\nTesting with {len(test_urls)} products")
    print("="*60)
    
    success_count = 0
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}] Scraping: {url}")
        
        product_data = scraper.scrape_product(url)
        
        if product_data:
            scraper.save_product(product_data)
            success_count += 1
            print(f"  ✓ {product_data['name'][:50]}...")
            print(f"    Price: {product_data['price_gross']} (gross) / {product_data['price_net']} (net)")
            print(f"    Manufacturer: {product_data['manufacturer']}")
            print(f"    EAN: {product_data['ean']}")
        else:
            print(f"  ✗ Failed to scrape")
    
    print(f"\n{'='*60}")
    print(f"Results: {success_count}/{len(test_urls)} products scraped successfully")
    print(f"Output file: {scraper.get_output_file()}")
    print(f"{'='*60}")
    
    # Show CSV content
    print("\nCSV Output Preview:")
    with open(scraper.get_output_file(), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            print(f"\nProduct {i}:")
            for key, value in row.items():
                if value:  # Only show non-empty fields
                    print(f"  {key}: {value[:80] if len(value) > 80 else value}")


if __name__ == "__main__":
    test_batch_scraping()
