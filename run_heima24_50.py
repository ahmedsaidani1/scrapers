"""
Run Heima24 scraper with 50 products limit
"""
import sys
import time
from heima24_scraper import Heima24Scraper
from google_sheets_helper import push_data
from config import SHEET_IDS

def run_limited_scrape(limit=50):
    """Run scraper with product limit."""
    
    print("="*70)
    print(f"HEIMA24 SCRAPER - LIMITED TO {limit} PRODUCTS")
    print("="*70)
    
    scraper = Heima24Scraper()
    start_time = time.time()
    
    # Get all product URLs
    print("\nFetching product URLs from sitemap...")
    all_urls = scraper.get_product_urls()
    
    print(f"Total products available: {len(all_urls)}")
    print(f"Scraping first {limit} products...")
    print("="*70)
    
    # Limit to first N products
    urls_to_scrape = all_urls[:limit]
    
    success_count = 0
    failed_count = 0
    
    for i, url in enumerate(urls_to_scrape, 1):
        print(f"\n[{i}/{limit}] {url}")
        
        try:
            product_data = scraper.scrape_product(url)
            
            if product_data:
                scraper.save_product(product_data)
                success_count += 1
                print(f"  ✓ {product_data['name'][:60]}...")
                print(f"    Price: €{product_data['price_gross']} | Article: {product_data['article_number']}")
            else:
                failed_count += 1
                print(f"  ✗ Failed to extract data")
        
        except Exception as e:
            failed_count += 1
            print(f"  ✗ Error: {e}")
        
        # Rate limiting
        scraper._random_delay()
    
    elapsed_time = time.time() - start_time
    
    # Summary
    print("\n" + "="*70)
    print("SCRAPING SUMMARY")
    print("="*70)
    print(f"Total scraped: {success_count}/{limit}")
    print(f"Failed: {failed_count}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"Average time per product: {elapsed_time/limit:.2f} seconds")
    print(f"Output file: {scraper.get_output_file()}")
    
    # Estimate for full scrape
    if len(all_urls) > limit:
        estimated_total_time = (elapsed_time / limit) * len(all_urls)
        hours = estimated_total_time / 3600
        print(f"\nEstimated time for all {len(all_urls)} products: {hours:.1f} hours")
    
    # Push to Google Sheets
    if success_count > 0:
        print("\n" + "="*70)
        print("PUSHING TO GOOGLE SHEETS")
        print("="*70)
        
        sheet_id = SHEET_IDS.get("heima24")
        
        if sheet_id and sheet_id != "TBD":
            print(f"Sheet ID: {sheet_id}")
            print("Uploading data...")
            
            if push_data(sheet_id, scraper.get_output_file()):
                print("\n✓ Successfully pushed to Google Sheets!")
                print(f"View here: https://docs.google.com/spreadsheets/d/{sheet_id}")
            else:
                print("\n✗ Failed to push to Google Sheets")
        else:
            print("⚠ No Google Sheet ID configured")
    
    print("\n" + "="*70)
    
    return success_count


if __name__ == "__main__":
    # You can change the limit here
    limit = 50
    
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except:
            print(f"Invalid limit, using default: {limit}")
    
    run_limited_scrape(limit)
