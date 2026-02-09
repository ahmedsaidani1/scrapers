"""
Run All Scrapers Sequentially and Push to Google Sheets
Executes all 9 working scrapers one after another
"""
import time
from datetime import datetime

# Import all scrapers
from meinhausshop_scraper import MeinHausShopScraper
from heima24_scraper import Heima24Scraper
from sanundo_scraper import SanundoScraper
from heizungsdiscount24_scraper import Heizungsdiscount24Scraper
from wolfonlineshop_scraper import WolfonlineshopScraper
from st_shop24_scraper import StShop24Scraper
from selfio_scraper import SelfioScraper
from pumpe24_scraper import Pumpe24Scraper
from wasserpumpe_scraper import WasserpumpeScraper

from google_sheets_helper import push_data
from config import SHEET_IDS, CONCURRENT_WORKERS


def run_scraper(scraper_name, scraper_class, max_products=None):
    """
    Run a single scraper and push to Google Sheets
    
    Args:
        scraper_name: Name of the scraper
        scraper_class: Scraper class to instantiate
        max_products: Maximum products to scrape (None for all)
    
    Returns:
        dict: Results of the scraping operation
    """
    start_time = time.time()
    
    try:
        print(f"\n{'='*70}")
        print(f"[{scraper_name.upper()}] Starting scraper...")
        print(f"{'='*70}")
        
        # Initialize and run scraper
        scraper = scraper_class()
        
        if max_products:
            success_count = scraper.run(max_products=max_products, concurrent_workers=CONCURRENT_WORKERS)
        else:
            success_count = scraper.run(concurrent_workers=CONCURRENT_WORKERS)
        
        elapsed_time = time.time() - start_time
        
        print(f"\n[{scraper_name.upper()}] Scraping completed!")
        print(f"  - Products scraped: {success_count}")
        print(f"  - Time taken: {elapsed_time:.2f} seconds")
        
        # Push to Google Sheets
        if success_count > 0:
            sheet_id = SHEET_IDS.get(scraper_name)
            
            if sheet_id and sheet_id != "TBD":
                print(f"[{scraper_name.upper()}] Pushing to Google Sheets...")
                
                if push_data(sheet_id, scraper.get_output_file()):
                    print(f"[{scraper_name.upper()}] ✓ Successfully pushed to Google Sheets!")
                    print(f"  - Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}")
                else:
                    print(f"[{scraper_name.upper()}] ✗ Failed to push to Google Sheets")
            else:
                print(f"[{scraper_name.upper()}] ⚠ No Google Sheet ID configured")
        
        return {
            'scraper': scraper_name,
            'success': True,
            'products': success_count,
            'time': elapsed_time,
            'error': None
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n[{scraper_name.upper()}] ✗ Error: {e}")
        
        return {
            'scraper': scraper_name,
            'success': False,
            'products': 0,
            'time': elapsed_time,
            'error': str(e)
        }


def main():
    """Main execution - runs all scrapers sequentially"""
    
    print("\n" + "="*70)
    print("RUNNING ALL SCRAPERS SEQUENTIALLY")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Define all scrapers to run
    # Format: (scraper_name, scraper_class, max_products)
    # Set max_products=None to scrape all products
    scrapers = [
        ('meinhausshop', MeinHausShopScraper, None),
        ('heima24', Heima24Scraper, None),
        ('sanundo', SanundoScraper, None),
        ('heizungsdiscount24', Heizungsdiscount24Scraper, None),
        ('wolfonlineshop', WolfonlineshopScraper, None),
        ('st_shop24', StShop24Scraper, None),
        ('selfio', SelfioScraper, None),
        ('pumpe24', Pumpe24Scraper, None),
        ('wasserpumpe', WasserpumpeScraper, None),
    ]
    
    start_time = time.time()
    results = []
    
    print(f"\nScraping {len(scrapers)} websites sequentially...\n")
    
    # Run scrapers one by one
    for i, (name, scraper_class, max_products) in enumerate(scrapers, 1):
        print(f"\n[{i}/{len(scrapers)}] Processing {name}...")
        result = run_scraper(name, scraper_class, max_products)
        results.append(result)
    
    # Calculate summary statistics
    total_time = time.time() - start_time
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    total_products = sum(r['products'] for r in results)
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    print(f"Successful scrapers: {successful}/{len(scrapers)}")
    print(f"Failed scrapers: {failed}/{len(scrapers)}")
    print(f"Total products scraped: {total_products:,}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Detailed results
    print("\n" + "="*70)
    print("DETAILED RESULTS")
    print("="*70)
    
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"\n{status} {result['scraper'].upper()}")
        print(f"  Products: {result['products']:,}")
        print(f"  Time: {result['time']:.2f}s")
        if result['error']:
            print(f"  Error: {result['error']}")
    
    print("\n" + "="*70)
    print("ALL SCRAPERS COMPLETED!")
    print("="*70)


if __name__ == "__main__":
    main()
