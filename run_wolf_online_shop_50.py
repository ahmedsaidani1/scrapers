"""
Run Wolf-Online-Shop scraper with limit of 50 products
"""
from wolf_online_shop_scraper import WolfOnlineShopScraper
from google_sheets_helper import push_data
from config import SHEET_IDS

def main():
    print("=" * 60)
    print("Wolf-Online-Shop Scraper - Limited Run (50 products)")
    print("=" * 60)
    
    scraper = WolfOnlineShopScraper()
    
    # Run with 50 product limit
    success_count = scraper.run(max_products=50)
    
    print(f"\n{'='*60}")
    print(f"Scraping completed: {success_count} products")
    print(f"Output file: {scraper.get_output_file()}")
    print(f"{'='*60}")
    
    # Ask about Google Sheets push
    if success_count > 0:
        sheet_id = SHEET_IDS.get("wolf_online_shop")
        
        if sheet_id and sheet_id != "TBD":
            response = input("\nPush data to Google Sheets? (y/n): ")
            if response.lower() == 'y':
                print("Pushing to Google Sheets...")
                if push_data(sheet_id, scraper.get_output_file()):
                    print("✓ Successfully pushed to Google Sheets")
                else:
                    print("✗ Failed to push to Google Sheets")
        else:
            print("\n⚠ No Google Sheet ID configured for wolf_online_shop")
            print("  Update SHEET_IDS in config.py to enable Google Sheets integration")

if __name__ == "__main__":
    main()
