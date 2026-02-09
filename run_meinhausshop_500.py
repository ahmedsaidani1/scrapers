"""
Run meinhausshop scraper with 500 products limit and push to Google Sheets
"""
from meinhausshop_scraper import MeinHausShopScraper
from google_sheets_helper import push_data
from config import SHEET_IDS

def main():
    print("="*70)
    print("Running meinhausshop scraper (500 products)")
    print("="*70)
    
    # Initialize scraper
    scraper = MeinHausShopScraper()
    
    # Run with 500 product limit
    success_count = scraper.run(max_products=500, concurrent_workers=10)
    
    print(f"\n✓ Scraped {success_count} products")
    
    # Push to Google Sheets
    if success_count > 0:
        sheet_id = SHEET_IDS.get('meinhausshop')
        
        if sheet_id and sheet_id != "TBD":
            print(f"\nPushing data to Google Sheets...")
            if push_data(sheet_id, scraper.get_output_file()):
                print("✓ Successfully pushed to Google Sheets")
                print(f"  Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}")
            else:
                print("✗ Failed to push to Google Sheets")
        else:
            print(f"\n⚠ No Google Sheet ID configured for meinhausshop")
    
    print(f"\n{'='*70}")
    print(f"Completed: {success_count} products scraped and pushed")
    print(f"Output: {scraper.get_output_file()}")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
