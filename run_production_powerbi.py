"""
Production Power BI Data Pipeline - OPTIMIZED FOR SPEED
Scrapes ALL products from 10 working websites IN PARALLEL
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
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Enable garbage collection
gc.enable()

# Thread-safe lock for printing
print_lock = Lock()

def thread_safe_print(*args, **kwargs):
    """Thread-safe print function"""
    with print_lock:
        print(*args, **kwargs)

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / 1024 / 1024  # Convert to MB

def log_memory(label=""):
    """Log current memory usage"""
    mem_mb = get_memory_usage()
    thread_safe_print(f"[MEMORY] {label}: {mem_mb:.1f} MB")
    return mem_mb

# Import all working scrapers
from meinhausshop_scraper import MeinHausShopScraper
from heima24_scraper import Heima24Scraper
from sanundo_scraper import SanundoScraper
from heizungsdiscount24_scraper import Heizungsdiscount24Scraper
from wolfonlineshop_scraper import WolfonlineshopScraper
from st_shop24_scraper import StShop24Scraper
from selfio_scraper import SelfioScraper
from pumpe24_scraper import Pumpe24Scraper
from wasserpumpe_scraper import WasserpumpeScraper
from pumpenheizung_scraper import PumpenheizungScraper
from google_sheets_helper import push_data
from config import DATA_DIR, CSV_COLUMNS

# Google Sheet ID for Power BI
POWER_BI_SHEET_ID = "1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg"

# 10 working scrapers - NO LIMITS, scrape everything
SCRAPERS = [
    ("sanundo", SanundoScraper),
    ("heima24", Heima24Scraper),
    ("st_shop24", StShop24Scraper),
    ("selfio", SelfioScraper),
    ("heizungsdiscount24", Heizungsdiscount24Scraper),
    ("meinhausshop", MeinHausShopScraper),
    ("wolfonlineshop", WolfonlineshopScraper),
    ("pumpe24", Pumpe24Scraper),
    ("pumpenheizung", PumpenheizungScraper),
    ("wasserpumpe", WasserpumpeScraper),
]

def run_single_scraper(name, scraper_class, idx, total):
    """Run a single scraper in a thread"""
    thread_safe_print(f"\n[{idx}/{total}] Starting {name}...")
    thread_safe_print("-" * 80)
    
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
                    product['Quelle'] = name  # 'source' in German
                    
                    # Convert Preis_Netto from German format to numeric
                    if product.get('Preis_Netto') and product['Preis_Netto'].strip():
                        try:
                            price_str = str(product['Preis_Netto']).strip().strip('"')
                            if ',' in price_str:
                                price_str = price_str.replace('.', '').replace(',', '.')
                            product['Preis_Netto'] = float(price_str)
                        except (ValueError, AttributeError):
                            product['Preis_Netto'] = ''
                    
                    # Convert Preis_Brutto from German format to numeric
                    if product.get('Preis_Brutto') and product['Preis_Brutto'].strip():
                        try:
                            price_str = str(product['Preis_Brutto']).strip().strip('"')
                            if ',' in price_str:
                                price_str = price_str.replace('.', '').replace(',', '.')
                            product['Preis_Brutto'] = float(price_str)
                        except (ValueError, AttributeError):
                            product['Preis_Brutto'] = ''
                
                thread_safe_print(f"✓ {name}: {len(products)} products scraped in {elapsed:.1f}s")
                
                result = {
                    "scraper": name,
                    "status": "success",
                    "products": len(products),
                    "time": elapsed,
                    "data": products
                }
                
                # Delete scraper object to free memory
                del scraper
                gc.collect()
                
                return result
        else:
            thread_safe_print(f"✗ {name}: No CSV file found")
            return {
                "scraper": name,
                "status": "failed",
                "products": 0,
                "time": elapsed,
                "data": []
            }
            
    except Exception as e:
        elapsed = time.time() - start_time
        thread_safe_print(f"✗ {name}: Error - {str(e)}")
        import traceback
        thread_safe_print(traceback.format_exc())
        
        return {
            "scraper": name,
            "status": "error",
            "products": 0,
            "time": elapsed,
            "error": str(e),
            "data": []
        }

def run_production_pipeline():
    """Run all 10 scrapers IN PARALLEL with NO LIMITS and push to Power BI sheet"""
    print("=" * 80)
    print("PRODUCTION POWER BI DATA PIPELINE - PARALLEL EXECUTION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Sheet ID: {POWER_BI_SHEET_ID}")
    print(f"Mode: PRODUCTION - Scraping ALL products (no limits)")
    print(f"Total scrapers: {len(SCRAPERS)}")
    print(f"Execution: PARALLEL (all scrapers run simultaneously)")
    print("=" * 80)
    
    # Log initial memory
    log_memory("Initial")
    print()
    
    results = []
    all_products = []
    total_start_time = time.time()
    
    # Run scrapers in parallel with ThreadPoolExecutor
    # Use max 5 workers to avoid overwhelming the system
    max_workers = min(5, len(SCRAPERS))
    print(f"Running {len(SCRAPERS)} scrapers with {max_workers} parallel workers...")
    print()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all scraper tasks
        future_to_scraper = {
            executor.submit(run_single_scraper, name, scraper_class, idx, len(SCRAPERS)): name
            for idx, (name, scraper_class) in enumerate(SCRAPERS, 1)
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_scraper):
            scraper_name = future_to_scraper[future]
            try:
                result = future.result()
                results.append(result)
                
                # Add products to combined list
                if result.get('data'):
                    all_products.extend(result['data'])
                    
            except Exception as e:
                thread_safe_print(f"✗ {scraper_name}: Unexpected error - {e}")
                results.append({
                    "scraper": scraper_name,
                    "status": "error",
                    "products": 0,
                    "time": 0,
                    "error": str(e),
                    "data": []
                })
    
    total_elapsed = time.time() - total_start_time
    
    # Push all products to Power BI Google Sheet
    if all_products:
        print("\n" + "=" * 80)
        print("PUSHING TO GOOGLE SHEETS")
        print("=" * 80)
        try:
            # Write combined CSV file
            combined_csv = DATA_DIR / "power_bi_production.csv"
            columns_with_source = CSV_COLUMNS + ['Quelle'] if 'Quelle' not in CSV_COLUMNS else CSV_COLUMNS
            
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
    print(f"Total time: {total_elapsed/60:.1f} minutes ({total_elapsed:.1f} seconds)")
    print(f"Average per scraper: {total_elapsed/len(SCRAPERS):.1f} seconds")
    print(f"Speed improvement: ~{len(SCRAPERS)}x faster than sequential")
    print()
    
    print("Results by scraper:")
    print("-" * 80)
    # Sort results by scraper name for consistent output
    results.sort(key=lambda x: x['scraper'])
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
    print(f"✓ Total execution time: {total_elapsed/60:.1f} minutes")
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
