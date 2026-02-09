"""
Run Glo24 scraper with 50 products limit (Cloudscraper-based)
"""
import sys
import time
from glo24_scraper import Glo24Scraper
from google_sheets_helper import push_data
from config import SHEET_IDS

def run_limited_scrape(limit=50):
    """Run scraper with product limit."""
    
    print("="*70)
    print(f"GLO24 SCRAPER (CLOUDSCRAPER) - LIMITED TO {limit} PRODUCTS")
    print("="*70)
    
    scraper = Glo24Scraper()
    start_time = time.time()
    
    success_count = scraper.run(max_products=limit)
    
    elapsed_time = time.time() - start_time
    
    # Summary
    print("\n" + "="*70)
    print("SCRAPING SUMMARY")
    print("="*70)
    print(f"Total scraped: {success_count}/{limit}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    if success_count > 0:
        print(f"Average time per product: {elapsed_time/success_count:.2f} seconds")
    print(f"Output file: {scraper.get_output_file()}")
    
    # Push to Google Sheets
    if success_count > 0:
        print("\n" + "="*70)
        print("PUSHING TO GOOGLE SHEETS")
        print("="*70)
        
        sheet_id = SHEET_IDS.get("glo24")
        
        if sheet_id and sheet_id != "TBD":
            print(f"Sheet ID: {sheet_id}")
            print("Uploading data...")
            
            if push_data(sheet_id, scraper.get_output_file()):
                print("\n✓ Successfully pushed to Google Sheets!")
                print(f"View here: https://docs.google.com/spreadsheets/d/{sheet_id}")
            else:
                print("\n✗ Failed to push to Google Sheets")
        else:
            print("⚠ No Google Sheet ID configured - please add to config.py")
    
    print("\n" + "="*70)
    
    return success_count


if __name__ == "__main__":
    limit = 50
    
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except:
            print(f"Invalid limit, using default: {limit}")
    
    run_limited_scrape(limit)
