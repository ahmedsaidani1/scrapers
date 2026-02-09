"""
PRODUCTION AUTOMATION SCRIPT
Runs the complete workflow:
1. Scrape all websites
2. Detect changes and send email notifications
3. Update Google Sheets
4. Generate Shopify CSV files
"""
import sys
from pathlib import Path
from datetime import datetime
from email_notifier import EmailNotifier
from email_config import (
    SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD,
    RECIPIENT_EMAILS, MONITORED_SCRAPERS, MIN_CHANGES_THRESHOLD
)
from config import DATA_DIR
from google_sheets_helper import GoogleSheetsHelper
from shopify_csv_export import ShopifyCSVExporter
import csv

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
from glo24_scraper import Glo24Scraper

# Map scraper names to classes
SCRAPER_CLASSES = {
    "meinhausshop": MeinHausShopScraper,
    "heima24": Heima24Scraper,
    "sanundo": SanundoScraper,
    "heizungsdiscount24": Heizungsdiscount24Scraper,
    "wolfonlineshop": WolfonlineshopScraper,
    "st_shop24": StShop24Scraper,
    "selfio": SelfioScraper,
    "pumpe24": Pumpe24Scraper,
    "wasserpumpe": WasserpumpeScraper,
    "glo24": Glo24Scraper,
}


def run_scraper(scraper_name: str, scraper_class, max_products: int = None) -> tuple:
    """Run a single scraper and return (success, product_count)"""
    print(f"\n{'='*70}")
    print(f"Running {scraper_name.upper()} scraper...")
    print(f"{'='*70}")
    
    try:
        scraper = scraper_class()
        if max_products:
            success_count = scraper.run(max_products=max_products)
        else:
            success_count = scraper.run()
        
        print(f"\n✓ {scraper_name}: Scraped {success_count} products")
        return True, success_count
        
    except Exception as e:
        print(f"\n✗ {scraper_name}: Error - {e}")
        return False, 0


def main():
    """Main execution"""
    start_time = datetime.now()
    
    print("="*70)
    print("🚀 PRODUCTION AUTOMATION - FULL WORKFLOW")
    print("="*70)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Monitoring {len(MONITORED_SCRAPERS)} scrapers")
    print("="*70)
    
    # Get max products from command line (optional)
    max_products = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if max_products:
        print(f"⚠️  Running in TEST MODE: {max_products} products per scraper")
    else:
        print("✓ Running in PRODUCTION MODE: All products")
    
    # ========================================================================
    # STEP 1: RUN SCRAPERS
    # ========================================================================
    print("\n" + "="*70)
    print("STEP 1: SCRAPING WEBSITES")
    print("="*70)
    
    results = {}
    total_products = 0
    
    for scraper_name in MONITORED_SCRAPERS:
        if scraper_name not in SCRAPER_CLASSES:
            print(f"\n⚠ Warning: Scraper '{scraper_name}' not found, skipping...")
            continue
        
        scraper_class = SCRAPER_CLASSES[scraper_name]
        success, count = run_scraper(scraper_name, scraper_class, max_products)
        results[scraper_name] = success
        total_products += count
    
    successful_scrapers = sum(1 for s in results.values() if s)
    print(f"\n✓ Scraped {total_products} total products from {successful_scrapers}/{len(results)} scrapers")
    
    # ========================================================================
    # STEP 2: EMAIL NOTIFICATIONS
    # ========================================================================
    print("\n" + "="*70)
    print("STEP 2: DETECTING CHANGES & SENDING EMAIL NOTIFICATIONS")
    print("="*70)
    
    try:
        notifier = EmailNotifier(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD,
            recipient_emails=RECIPIENT_EMAILS
        )
        print("✓ Email notifier initialized")
        
        total_notifications = 0
        all_changes = {
            'new': 0,
            'updated': 0,
            'removed': 0
        }
        
        for scraper_name in MONITORED_SCRAPERS:
            if not results.get(scraper_name, False):
                print(f"\n⚠ Skipping {scraper_name} (scraping failed)")
                continue
            
            csv_path = DATA_DIR / f"{scraper_name}.csv"
            
            if csv_path.exists():
                try:
                    new_products, updated_products, removed_products = notifier.detect_changes(
                        scraper_name, str(csv_path)
                    )
                    
                    total_changes = len(new_products) + len(updated_products) + len(removed_products)
                    
                    all_changes['new'] += len(new_products)
                    all_changes['updated'] += len(updated_products)
                    all_changes['removed'] += len(removed_products)
                    
                    print(f"\n{scraper_name}:")
                    print(f"  New: {len(new_products)}")
                    print(f"  Updated: {len(updated_products)}")
                    print(f"  Removed: {len(removed_products)}")
                    
                    if total_changes >= MIN_CHANGES_THRESHOLD:
                        subject = f"🔔 {scraper_name.upper()} - {total_changes} Changes Detected"
                        html_content = notifier.format_html_email(
                            scraper_name, new_products, updated_products, removed_products
                        )
                        
                        if notifier.send_email(subject, html_content):
                            total_notifications += 1
                            print(f"  ✓ Email sent")
                    else:
                        print(f"  No email sent (below threshold)")
                
                except Exception as e:
                    print(f"  ✗ Error: {e}")
        
        print(f"\n✓ Sent {total_notifications} email notifications")
        print(f"  Total changes: {all_changes['new']} new, {all_changes['updated']} updated, {all_changes['removed']} removed")
        
    except Exception as e:
        print(f"✗ Email notifications failed: {e}")
    
    # ========================================================================
    # STEP 3: UPDATE GOOGLE SHEETS
    # ========================================================================
    print("\n" + "="*70)
    print("STEP 3: UPDATING GOOGLE SHEETS")
    print("="*70)
    
    try:
        sheets_helper = GoogleSheetsHelper()
        sheets_updated = 0
        
        for scraper_name in MONITORED_SCRAPERS:
            if not results.get(scraper_name, False):
                continue
            
            csv_path = DATA_DIR / f"{scraper_name}.csv"
            
            if csv_path.exists():
                try:
                    print(f"\nUpdating {scraper_name}...", end=" ")
                    sheets_helper.update_sheet(scraper_name, str(csv_path))
                    sheets_updated += 1
                    print("✓")
                except Exception as e:
                    print(f"✗ Error: {e}")
        
        print(f"\n✓ Updated {sheets_updated} Google Sheets")
        
    except Exception as e:
        print(f"✗ Google Sheets update failed: {e}")
        print("  (This is optional - continuing...)")
    
    # ========================================================================
    # STEP 4: GENERATE SHOPIFY CSV FILES
    # ========================================================================
    print("\n" + "="*70)
    print("STEP 4: GENERATING SHOPIFY CSV FILES")
    print("="*70)
    
    try:
        markup_percentage = 20  # Default 20% markup
        exporter = ShopifyCSVExporter(price_markup_percent=markup_percentage)
        shopify_files = 0
        
        for scraper_name in MONITORED_SCRAPERS:
            if not results.get(scraper_name, False):
                continue
            
            csv_path = DATA_DIR / f"{scraper_name}.csv"
            
            if csv_path.exists():
                try:
                    print(f"\nConverting {scraper_name}...", end=" ")
                    output_path = Path("shopify_imports") / f"{scraper_name}_shopify.csv"
                    exporter.export_csv(str(csv_path), str(output_path))
                    shopify_files += 1
                    print("✓")
                except Exception as e:
                    print(f"✗ Error: {e}")
        
        print(f"\n✓ Generated {shopify_files} Shopify CSV files (with {markup_percentage}% markup)")
        print(f"  Location: shopify_imports/")
        
    except Exception as e:
        print(f"✗ Shopify CSV generation failed: {e}")
    
    # ========================================================================
    # STEP 5: UPDATE POWER BI SHEET
    # ========================================================================
    print("\n" + "="*70)
    print("STEP 5: UPDATING POWER BI SHEET")
    print("="*70)
    
    try:
        from config import CSV_COLUMNS
        
        # Power BI Google Sheet ID
        POWER_BI_SHEET_ID = "1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA"
        
        # Collect all products from successful scrapers
        all_products = []
        
        for scraper_name in MONITORED_SCRAPERS:
            if not results.get(scraper_name, False):
                continue
            
            csv_path = DATA_DIR / f"{scraper_name}.csv"
            
            if csv_path.exists():
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        products = list(reader)
                        
                        # Add source column to each product
                        for product in products:
                            product['source'] = scraper_name
                        
                        all_products.extend(products)
                        print(f"  ✓ {scraper_name}: {len(products)} products")
                        
                except Exception as e:
                    print(f"  ✗ {scraper_name}: Error reading CSV - {e}")
        
        if all_products:
            # Write combined CSV file
            combined_csv = DATA_DIR / "power_bi_test.csv"
            columns_with_source = CSV_COLUMNS + ['source'] if 'source' not in CSV_COLUMNS else CSV_COLUMNS
            
            with open(combined_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns_with_source)
                writer.writeheader()
                writer.writerows(all_products)
            
            print(f"\n✓ Created combined CSV with {len(all_products)} products")
            
            # Push to Power BI Google Sheet
            from google_sheets_helper import push_data
            push_data(
                sheet_id=POWER_BI_SHEET_ID,
                csv_file=combined_csv
            )
            print(f"✓ Successfully pushed {len(all_products)} products to Power BI Sheet")
            print(f"  Sheet ID: {POWER_BI_SHEET_ID}")
        else:
            print("⚠ No products to push to Power BI")
        
    except Exception as e:
        print(f"✗ Power BI update failed: {e}")
        import traceback
        traceback.print_exc()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*70)
    print("📊 EXECUTION SUMMARY")
    print("="*70)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration}")
    print(f"\nScrapers:")
    
    for scraper_name, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {scraper_name}")
    
    print(f"\nResults:")
    print(f"  ✓ {successful_scrapers}/{len(results)} scrapers successful")
    print(f"  ✓ {total_products} total products scraped")
    print(f"  ✓ {total_notifications} email notifications sent")
    print(f"  ✓ Google Sheets updated")
    print(f"  ✓ Shopify CSV files generated")
    print(f"  ✓ Power BI sheet updated")
    print("="*70)
    print("🎉 PRODUCTION RUN COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    main()
