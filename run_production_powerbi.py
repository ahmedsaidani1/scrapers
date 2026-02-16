"""
Production Power BI Data Pipeline - MEMORY OPTIMIZED
Scrapes ALL products from 10 working websites IN PARALLEL
Pushes to Google Sheet: 1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg
Runs on Render with automatic scheduling
Memory optimized for 2GB instances - streams data to disk instead of accumulating in memory
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

# Thread-safe locks
print_lock = Lock()
csv_lock = Lock()  # Lock for CSV writing

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

def convert_price(price_str):
    """Optimized price conversion from German format to float"""
    if not price_str or not price_str.strip():
        return ''
    try:
        price_str = str(price_str).strip().strip('"')
        if ',' in price_str:
            # German format: "1.234,56" -> 1234.56
            price_str = price_str.replace('.', '').replace(',', '.')
        return float(price_str)
    except (ValueError, AttributeError):
        return ''

def process_and_write_products(name, csv_file, combined_csv_path, columns_with_source, header_written):
    """
    Process products from scraper CSV and write them incrementally to combined CSV.
    Optimized for speed with larger chunks and reduced I/O operations.
    
    Returns:
        Tuple of (product_count, header_written_flag)
    """
    product_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Process products in chunks (balanced for memory and speed)
            chunk = []
            chunk_size = 500  # Balanced chunk size for memory safety
            
            for product in reader:
                # Add source column
                product['Quelle'] = name
                
                # Optimized price conversion (only convert if value exists)
                if product.get('Preis_Netto'):
                    product['Preis_Netto'] = convert_price(product['Preis_Netto'])
                
                if product.get('Preis_Brutto'):
                    product['Preis_Brutto'] = convert_price(product['Preis_Brutto'])
                
                chunk.append(product)
                product_count += 1
                
                # Write chunk when it reaches chunk_size
                if len(chunk) >= chunk_size:
                    with csv_lock:
                        with open(combined_csv_path, 'a', newline='', encoding='utf-8') as combined_f:
                            writer = csv.DictWriter(combined_f, fieldnames=columns_with_source)
                            if not header_written[0]:
                                writer.writeheader()
                                header_written[0] = True
                            writer.writerows(chunk)
                    chunk = []
                    # GC every 3 chunks to balance memory and performance
                    if product_count % (chunk_size * 3) == 0:
                        gc.collect()
            
            # Write remaining products
            if chunk:
                with csv_lock:
                    with open(combined_csv_path, 'a', newline='', encoding='utf-8') as combined_f:
                        writer = csv.DictWriter(combined_f, fieldnames=columns_with_source)
                        if not header_written[0]:
                            writer.writeheader()
                            header_written[0] = True
                        writer.writerows(chunk)
                chunk = []
    
    except Exception as e:
        thread_safe_print(f"✗ Error processing products from {name}: {e}")
        import traceback
        thread_safe_print(traceback.format_exc())
    
    return product_count

def run_single_scraper(name, scraper_class, idx, total, combined_csv_path, columns_with_source, header_written):
    """Run a single scraper in a thread and write products incrementally"""
    thread_safe_print(f"\n[{idx}/{total}] Starting {name}...")
    thread_safe_print("-" * 80)
    
    start_time = time.time()
    mem_before = get_memory_usage()
    
    try:
        # Initialize scraper
        scraper = scraper_class()
        
        # Run scraper with NO LIMIT - scrape everything
        product_count = scraper.run(max_products=None)
        
        elapsed = time.time() - start_time
        
        # Delete scraper object immediately to free memory
        del scraper
        # Always GC after scraper to free memory aggressively
        gc.collect()
        
        mem_after_scrape = get_memory_usage()
        
        # Read the scraped products from CSV and write incrementally
        csv_file = DATA_DIR / f"{name}.csv"
        if csv_file.exists():
            # Process and write products incrementally
            processed_count = process_and_write_products(
                name, csv_file, combined_csv_path, columns_with_source, header_written
            )
            
            mem_after_process = get_memory_usage()
            
            thread_safe_print(f"✓ {name}: {processed_count} products scraped in {elapsed:.1f}s")
            thread_safe_print(f"  Memory: {mem_before:.1f}MB → {mem_after_scrape:.1f}MB → {mem_after_process:.1f}MB")
            
            result = {
                "scraper": name,
                "status": "success",
                "products": processed_count,
                "time": elapsed
            }
            
            # Clear CSV file reference
            del csv_file
            
            return result
        else:
            thread_safe_print(f"✗ {name}: No CSV file found")
            return {
                "scraper": name,
                "status": "failed",
                "products": 0,
                "time": elapsed
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
            "error": str(e)
        }

def run_production_pipeline():
    """Run all 10 scrapers IN PARALLEL with NO LIMITS and push to Power BI sheet"""
    print("=" * 80)
    print("PRODUCTION POWER BI DATA PIPELINE - OPTIMIZED FOR SPEED")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Sheet ID: {POWER_BI_SHEET_ID}")
    print(f"Mode: PRODUCTION - Scraping ALL products (no limits)")
    print(f"Total scrapers: {len(SCRAPERS)}")
    print(f"Strategy: Streaming + Batched Processing (memory safe for 2GB)")
    print("=" * 80)
    
    # Log initial memory
    log_memory("Initial")
    print()
    
    # Prepare combined CSV file path
    combined_csv = DATA_DIR / "power_bi_production.csv"
    
    # Remove existing combined CSV if it exists
    if combined_csv.exists():
        combined_csv.unlink()
        print("✓ Cleared existing combined CSV file")
    
    # Prepare columns with source
    columns_with_source = CSV_COLUMNS + ['Quelle'] if 'Quelle' not in CSV_COLUMNS else CSV_COLUMNS
    
    # Shared header flag (thread-safe list to pass by reference)
    header_written = [False]
    
    results = []
    total_products = 0
    total_start_time = time.time()
    
    # Process scrapers in batches to prevent memory overflow
    # With 2GB RAM, we need to be conservative
    batch_size = 3  # Process 3 scrapers at a time
    max_workers = min(batch_size, len(SCRAPERS))
    
    print(f"Running {len(SCRAPERS)} scrapers in batches of {batch_size} (memory safe)...")
    print(f"Chunk size: 500 products per write")
    print(f"Memory limit: 1800 MB (will GC aggressively if exceeded)")
    print()
    
    # Process scrapers in batches
    for batch_start in range(0, len(SCRAPERS), batch_size):
        batch_end = min(batch_start + batch_size, len(SCRAPERS))
        batch_scrapers = SCRAPERS[batch_start:batch_end]
        
        thread_safe_print(f"\n{'='*80}")
        thread_safe_print(f"Processing batch {batch_start//batch_size + 1}: {[name for name, _ in batch_scrapers]}")
        thread_safe_print(f"{'='*80}")
        log_memory(f"Before batch {batch_start//batch_size + 1}")
        
        with ThreadPoolExecutor(max_workers=len(batch_scrapers)) as executor:
            # Submit batch scraper tasks
            future_to_scraper = {
                executor.submit(run_single_scraper, name, scraper_class, batch_start + idx + 1, len(SCRAPERS), combined_csv, columns_with_source, header_written): name
                for idx, (name, scraper_class) in enumerate(batch_scrapers)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_scraper):
                scraper_name = future_to_scraper[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Track total products
                    if result.get('products'):
                        total_products += result['products']
                    
                    # Aggressive memory management
                    current_mem = get_memory_usage()
                    if current_mem > 1800:  # If over 1.8GB, force GC
                        thread_safe_print(f"⚠ High memory usage ({current_mem:.1f} MB) - forcing GC")
                        gc.collect()
                        time.sleep(1)  # Brief pause to let GC complete
                    
                    log_memory(f"After {scraper_name}")
                    
                    # Force GC after each scraper in batch to free memory
                    gc.collect()
                        
                except Exception as e:
                    thread_safe_print(f"✗ {scraper_name}: Unexpected error - {e}")
                    import traceback
                    thread_safe_print(traceback.format_exc())
                    results.append({
                        "scraper": scraper_name,
                        "status": "error",
                        "products": 0,
                        "time": 0,
                        "error": str(e)
                    })
        
        # Aggressive cleanup between batches
        gc.collect()
        time.sleep(2)  # Brief pause between batches to let system recover
        log_memory(f"After batch {batch_start//batch_size + 1}")
    
    total_elapsed = time.time() - total_start_time
    
    # Verify combined CSV was created and has data
    if combined_csv.exists() and total_products > 0:
        # Count actual rows in CSV (excluding header)
        with open(combined_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            actual_rows = sum(1 for row in reader) - 1  # Subtract header
        
        print("\n" + "=" * 80)
        print("PUSHING TO GOOGLE SHEETS")
        print("=" * 80)
        log_memory("Before Google Sheets upload")
        
        try:
            # Push to Google Sheets (the helper will read from CSV file)
            push_data(
                sheet_id=POWER_BI_SHEET_ID,
                csv_file=combined_csv
            )
            print(f"✓ Successfully pushed {actual_rows:,} products to Google Sheets")
            print(f"✓ Power BI will auto-refresh with new data")
            
            log_memory("After Google Sheets upload")
            
        except Exception as e:
            print(f"✗ Failed to push to Google Sheets: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("\n✗ No products scraped - pipeline failed")
        if not combined_csv.exists():
            print("  Combined CSV file was not created")
        if total_products == 0:
            print("  Total product count is 0")
        sys.exit(1)
    
    # Print summary
    print("\n" + "=" * 80)
    print("PRODUCTION PIPELINE SUMMARY")
    print("=" * 80)
    print(f"\nTotal products scraped: {total_products:,}")
    print(f"Total time: {total_elapsed/60:.1f} minutes ({total_elapsed:.1f} seconds)")
    
    # Calculate average scraper time (longest scraper determines total time in parallel)
    longest_scraper_time = max((r.get('time', 0) for r in results), default=0)
    avg_scraper_time = sum(r.get('time', 0) for r in results) / len(results) if results else 0
    estimated_sequential_time = sum(r.get('time', 0) for r in results)
    
    print(f"Average scraper time: {avg_scraper_time:.1f}s")
    print(f"Longest scraper time: {longest_scraper_time:.1f}s")
    if batch_size > 1 and estimated_sequential_time > 0:
        speedup = estimated_sequential_time / total_elapsed
        print(f"Estimated sequential time: {estimated_sequential_time/60:.1f} minutes")
        print(f"Speed improvement: ~{speedup:.1f}x faster with batched processing ({batch_size} per batch)")
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
    print(f"✓ Power BI Dashboard will auto-refresh with {total_products:,} products")
    print(f"✓ Total execution time: {total_elapsed/60:.1f} minutes")
    log_memory("Final")
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
