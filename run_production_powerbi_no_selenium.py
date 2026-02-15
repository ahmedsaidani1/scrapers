"""
Production Power BI Data Pipeline (No Selenium)
Scrapes ALL products from 8 working websites (excludes Selenium scrapers)
Pushes to Google Sheet: 1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg
Runs on Render with automatic scheduling
Memory optimized for 512MB instances
"""
import sys
import csv
import time
import os
import gc
import psutil
from datetime import datetime
from pathlib import Path

# Enable garbage collection
gc.enable()

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / 1024 / 1024  # Convert to MB

def log_memory(label=""):
    """Log current memory usage"""
    mem_mb = get_memory_usage()
    print(f"[MEMORY] {label}: {mem_mb:.1f} MB")
    return mem_mb

# Import working scrapers (NO SELENIUM)
from meinhausshop_scraper import MeinHausShopScraper
from heima24_scraper import Heima24Scraper
from sanundo_scraper import SanundoScraper
from heizungsdiscount24_scraper import Heizungsdiscount24Scraper
from wolfonlineshop_scraper import WolfonlineshopScraper
from st_shop24_scraper import StShop24Scraper
from selfio_scraper import SelfioScraper
from pumpe24_scraper import Pumpe24Scraper
from google_sheets_helper import push_data
from config import DATA_DIR, CSV_COLUMNS

# Google Sheet ID for Power BI
POWER_BI_SHEET_ID = "1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg"

# 8 working scrapers - NO SELENIUM (for Render compatibility)
# Ordered by memory usage: lightest first
SCRAPERS = [
    ("sanundo", SanundoScraper),              # Lightweight
    ("heima24", Heima24Scraper),              # Lightweight
    ("st_shop24", StShop24Scraper),           # Lightweight
    ("selfio", SelfioScraper),                # Lightweight
    ("heizungsdiscount24", Heizungsdiscount24Scraper),  # Medium
    ("meinhausshop", MeinHausShopScraper),    # Medium
    ("wolfonlineshop", WolfonlineshopScraper),# Medium
    ("pumpe24", Pumpe24Scraper),              # Medium
]

def run_production_pipeline():
    """Run all 8 scrapers with NO LIMITS and push to Power BI sheet"""
    print("=" * 80)
    print("PRODUCTION POWER BI DATA PIPELINE (NO SELENIUM)")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Sheet ID: {POWER_BI_SHEET_ID}")
    print(f"Mode: PRODUCTION - Scraping ALL products (no limits)")
    print(f"Total scrapers: {len(SCRAPERS)}")
    print(f"Note: Selenium scrapers (wasserpumpe, pumpenheizung) excluded for Render compatibility")
    print("=" * 80)
    
    # Log initial memory
    log_memory("Initial")
    print()
    
    results = []
    all_products = []
    total_start_time = time.time()
    
    for idx, (name, scraper_class) in enumerate(SCRAPERS, 1):
        print(f"\n[{idx}/{len(SCRAPERS)}] Running {name}...")
        print("-" * 80)
        
        # Log memory before scraper
        log_memory(f"Before {name}")
        
        start_time = time.time()
        
        try:
            # Initialize scraper
            scraper = scraper_class()
            
            # Run scraper with NO LIMIT - scrape everything
            product_count = scraper.run(max_products=None)
            
            elapsed = time.time() - start_time
            
            # Read the scraped products from CSV
            csv_file = DATA_DIR / f"{name}.csv"
            if csv_file.exists():
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    products = list(reader)
                    
                    # Add source column and convert prices to numbers
                    for product in products:
                        product['source'] = name
                        
                        # Convert price_net from German format to numeric
                        if product.get('price_net') and product['price_net'].strip():
                            try:
                                price_str = str(product['price_net']).strip().strip('"')
                                if ',' in price_str:
                                    price_str = price_str.replace('.', '').replace(',', '.')
                                product['price_net'] = float(price_str)
                            except (ValueError, AttributeError):
                                product['price_net'] = ''
                        
                        # Convert price_gross from German format to numeric
                        if product.get('price_gross') and product['price_gross'].strip():
                            try:
                                price_str = str(product['price_gross']).strip().strip('"')
                                if ',' in price_str:
                                    price_str = price_str.replace('.', '').replace(',', '.')
                                product['price_gross'] = float(price_str)
                            except (ValueError, AttributeError):
                                product['price_gross'] = ''
                    
                    all_products.extend(products)
                    
                    print(f"✓ {name}: {len(products)} products scraped in {elapsed:.1f}s")
                    
                    # Log memory after scraper
                    log_memory(f"After {name}")
                    
                    results.append({
                        "scraper": name,
                        "status": "success",
                        "products": len(products),
                        "time": elapsed
                    })
                    
                    # Clear products list to free memory
                    del products
            else:
                print(f"✗ {name}: No CSV file found")
                results.append({
                    "scraper": name,
                    "status": "failed",
                    "products": 0,
                    "time": elapsed
                })
            
            # Delete scraper object to free memory
            del scraper
            
            # Force garbage collection
            gc.collect()
            
            # Log memory after cleanup
            log_memory(f"After cleanup {name}")
                
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"✗ {name}: Error - {str(e)}")
            results.append({
                "scraper": name,
                "status": "error",
                "products": 0,
                "time": elapsed,
                "error": str(e)
            })
            
            # Clean up on error too
            gc.collect()
            log_memory(f"After error {name}")
    
    total_elapsed = time.time() - total_start_time
    
    # Push all products to Power BI Google Sheet
    if all_products:
        print("\n" + "=" * 80)
        print("PUSHING TO GOOGLE SHEETS")
        print("=" * 80)
        try:
            # Write combined CSV file
            combined_csv = DATA_DIR / "power_bi_production.csv"
            columns_with_source = CSV_COLUMNS + ['source'] if 'source' not in CSV_COLUMNS else CSV_COLUMNS
            
            with open(combined_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns_with_source)
                writer.writeheader()
                writer.writerows(all_products)
            
            print(f"✓ Created combined CSV with {len(all_products)} products")
            
            # Push to Google Sheets
            push_data(
                sheet_id=POWER_BI_SHEET_ID,
                csv_file=combined_csv
            )
            print(f"✓ Successfully pushed {len(all_products)} products to Google Sheets")
            print(f"✓ Power BI will auto-refresh with new data")
        except Exception as e:
            print(f"✗ Failed to push to Google Sheets: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("\n✗ No products scraped - pipeline failed")
        sys.exit(1)
    
    # Print summary
    print("\n" + "=" * 80)
    print("PRODUCTION PIPELINE SUMMARY")
    print("=" * 80)
    print(f"\nTotal products scraped: {len(all_products):,}")
    print(f"Total time: {total_elapsed/60:.1f} minutes")
    print(f"Average per scraper: {total_elapsed/len(SCRAPERS):.1f} seconds")
    print()
    
    print("Results by scraper:")
    print("-" * 80)
    for result in results:
        status_icon = "✓" if result["status"] == "success" else "✗"
        print(f"{status_icon} {result['scraper']:20s} | {result['products']:6,d} products | {result['time']:6.1f}s")
        if "error" in result:
            print(f"  Error: {result['error']}")
    
    print("\n" + "=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"\n✓ Data successfully pushed to Google Sheet: {POWER_BI_SHEET_ID}")
    print(f"✓ Power BI Dashboard will auto-refresh with {len(all_products):,} products")
    print("=" * 80)

if __name__ == "__main__":
    try:
        run_production_pipeline()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
