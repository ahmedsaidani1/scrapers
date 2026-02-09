"""
Power BI Test Data Generator
Scrapes 20 products from each of the 9 working websites
Pushes to Google Sheet: 1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA
"""
import sys
import csv
import time
from datetime import datetime
from pathlib import Path

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
from google_sheets_helper import push_data
from config import DATA_DIR, CSV_COLUMNS

# Google Sheet ID for Power BI testing
POWER_BI_SHEET_ID = "1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg"

# 9 working scrapers
SCRAPERS = [
    ("meinhausshop", MeinHausShopScraper),
    ("heima24", Heima24Scraper),
    ("sanundo", SanundoScraper),
    ("heizungsdiscount24", Heizungsdiscount24Scraper),
    ("wolfonlineshop", WolfonlineshopScraper),
    ("st_shop24", StShop24Scraper),
    ("selfio", SelfioScraper),
    ("pumpe24", Pumpe24Scraper),
    ("wasserpumpe", WasserpumpeScraper),
]

def run_power_bi_test():
    """Run all 9 scrapers with 20 products each and push to Power BI sheet"""
    print("=" * 80)
    print("POWER BI TEST DATA GENERATOR")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Sheet ID: {POWER_BI_SHEET_ID}")
    print(f"Products per scraper: 20")
    print(f"Total scrapers: {len(SCRAPERS)}")
    print(f"Expected total products: {len(SCRAPERS) * 20} = 180 products")
    print("=" * 80)
    print()
    
    results = []
    all_products = []
    
    for idx, (name, scraper_class) in enumerate(SCRAPERS, 1):
        print(f"\n[{idx}/{len(SCRAPERS)}] Running {name}...")
        print("-" * 80)
        
        start_time = time.time()
        
        try:
            # Initialize scraper
            scraper = scraper_class()
            
            # Run scraper with limit of 20 products
            product_count = scraper.run(max_products=20)
            
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
                        
                        # Convert price_net from German format (1.234,56) to numeric format
                        if product.get('price_net') and product['price_net'].strip():
                            try:
                                price_str = str(product['price_net']).strip().strip('"')
                                # Check if it's German format (has comma) or already numeric (has dot)
                                if ',' in price_str:
                                    # German format: remove thousand separators (.) and replace decimal comma with dot
                                    price_str = price_str.replace('.', '').replace(',', '.')
                                # Convert to float
                                product['price_net'] = float(price_str)
                            except (ValueError, AttributeError):
                                product['price_net'] = ''
                        
                        # Convert price_gross from German format (1.234,56) to numeric format
                        if product.get('price_gross') and product['price_gross'].strip():
                            try:
                                price_str = str(product['price_gross']).strip().strip('"')
                                # Check if it's German format (has comma) or already numeric (has dot)
                                if ',' in price_str:
                                    # German format: remove thousand separators (.) and replace decimal comma with dot
                                    price_str = price_str.replace('.', '').replace(',', '.')
                                # Convert to float
                                product['price_gross'] = float(price_str)
                            except (ValueError, AttributeError):
                                product['price_gross'] = ''
                    
                    all_products.extend(products)
                    
                    print(f"✓ {name}: {len(products)} products scraped in {elapsed:.1f}s")
                    results.append({
                        "scraper": name,
                        "status": "success",
                        "products": len(products),
                        "time": elapsed
                    })
            else:
                print(f"✗ {name}: No CSV file found")
                results.append({
                    "scraper": name,
                    "status": "failed",
                    "products": 0,
                    "time": elapsed
                })
                
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
    
    # Push all products to Power BI Google Sheet
    if all_products:
        print("\n" + "=" * 80)
        print("PUSHING TO GOOGLE SHEETS")
        print("=" * 80)
        try:
            # Write combined CSV file
            combined_csv = DATA_DIR / "power_bi_test.csv"
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
        except Exception as e:
            print(f"✗ Failed to push to Google Sheets: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal products scraped: {len(all_products)}")
    print(f"Target: {len(SCRAPERS) * 20}")
    print(f"Success rate: {(len(all_products) / (len(SCRAPERS) * 20)) * 100:.1f}%")
    print()
    
    print("Results by scraper:")
    print("-" * 80)
    for result in results:
        status_icon = "✓" if result["status"] == "success" else "✗"
        print(f"{status_icon} {result['scraper']:20s} | {result['products']:3d} products | {result['time']:6.1f}s")
        if "error" in result:
            print(f"  Error: {result['error']}")
    
    print("\n" + "=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print(f"✓ Data pushed to Google Sheet: {POWER_BI_SHEET_ID}")
    print()
    print("POWER BI SETUP (ONE-TIME ONLY):")
    print("=" * 80)
    print("Your client needs to set this up ONCE, then it auto-refreshes weekly:")
    print()
    print("1. Open Power BI Desktop")
    print("2. Get Data → Web")
    print("3. Paste this URL:")
    print(f"   https://docs.google.com/spreadsheets/d/{POWER_BI_SHEET_ID}/export?format=csv")
    print()
    print("4. Power BI will load the data with:")
    print("   ✓ Headers automatically recognized")
    print("   ✓ Numbers as numbers (sortable)")
    print()
    print("5. Click 'Load' (no transformation needed!)")
    print()
    print("6. Set up automatic refresh:")
    print("   - File → Options → Data Load")
    print("   - Configure refresh schedule (e.g., weekly)")
    print()
    print("That's it! Every week when you run this script, Power BI will")
    print("automatically refresh with the new data. No manual work needed!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        run_power_bi_test()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
