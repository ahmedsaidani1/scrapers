"""
Sync from Google Sheets to Shopify.
This runs AFTER your scrapers have pushed data to Google Sheets.

Flow:
1. Scrapers run → Push to Google Sheets (already automated)
2. This script: Pull from Sheets → Convert to CSV → Upload to Shopify
"""
import os
import sys
import csv
import time
from google_sheets_helper import GoogleSheetsHelper
from shopify_selenium_uploader import ShopifySeleniumUploader
from config import SHEET_IDS


def download_sheets_to_csv():
    """Download all Google Sheets to CSV files."""
    print("=" * 70)
    print("STEP 1: Downloading data from Google Sheets")
    print("=" * 70)
    
    helper = GoogleSheetsHelper()
    
    for scraper_name, sheet_id in SHEET_IDS.items():
        try:
            print(f"\nDownloading {scraper_name}...")
            
            # Read from sheet
            data = helper.read_sheet(sheet_id)
            
            if not data or len(data) < 2:  # Header + at least 1 row
                print(f"  ⚠ No data in {scraper_name}, skipping")
                continue
            
            # Save to CSV
            csv_file = f"data/{scraper_name}.csv"
            
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(data)
            
            print(f"  ✓ Saved {len(data)-1} products to {csv_file}")
            
        except Exception as e:
            print(f"  ✗ Error downloading {scraper_name}: {e}")
    
    print("\n✓ Download complete")


def convert_to_shopify_format(markup_percent=20):
    """Convert CSVs to Shopify format."""
    print("\n" + "=" * 70)
    print(f"STEP 2: Converting to Shopify format ({markup_percent}% markup)")
    print("=" * 70)
    
    from shopify_csv_export import ShopifyCSVExporter
    
    exporter = ShopifyCSVExporter(price_markup_percent=markup_percent)
    output_files = exporter.export_all_scrapers()
    
    print(f"\n✓ Converted {len(output_files)} files")
    return output_files


def upload_to_shopify(email, password, max_files=None):
    """Upload CSVs to Shopify using Selenium."""
    print("\n" + "=" * 70)
    print("STEP 3: Uploading to Shopify")
    print("=" * 70)
    
    uploader = ShopifySeleniumUploader(email, password)
    
    try:
        # Setup browser
        uploader.setup_driver(headless=True)  # Run in background
        
        # Login
        if not uploader.login():
            print("\n❌ Login failed!")
            return False
        
        # Upload all CSVs
        uploader.upload_all_csvs(max_files=max_files)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Upload error: {e}")
        return False
    finally:
        uploader.close()


def main():
    """Main execution."""
    print("=" * 70)
    print("SHOPIFY SYNC FROM GOOGLE SHEETS")
    print("=" * 70)
    
    # Get credentials
    email = os.getenv('SHOPIFY_EMAIL') or (sys.argv[1] if len(sys.argv) > 1 else None)
    password = os.getenv('SHOPIFY_PASSWORD') or (sys.argv[2] if len(sys.argv) > 2 else None)
    markup = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    
    if not email or not password:
        print("\n❌ Shopify credentials required!")
        print("\nUsage:")
        print("  python shopify_sync_from_sheets.py <email> <password> [markup%]")
        print("\nExample:")
        print("  python shopify_sync_from_sheets.py admin@tbbt.de mypass 20")
        print("\nOr set environment variables:")
        print("  set SHOPIFY_EMAIL=admin@tbbt.de")
        print("  set SHOPIFY_PASSWORD=mypass")
        sys.exit(1)
    
    try:
        # Step 1: Download from Google Sheets
        download_sheets_to_csv()
        
        # Step 2: Convert to Shopify format
        convert_to_shopify_format(markup_percent=markup)
        
        # Step 3: Upload to Shopify
        if upload_to_shopify(email, password):
            print("\n" + "=" * 70)
            print("✓ SYNC COMPLETE!")
            print("=" * 70)
            print("\nProducts have been uploaded to Shopify as drafts.")
            print("Review them in Shopify admin before publishing.")
        else:
            print("\n❌ Sync failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
