"""
Test which Shopify integration solution will work for you.
"""
import os
import sys

print("=" * 70)
print("SHOPIFY INTEGRATION - SOLUTION TESTER")
print("=" * 70)

# Test 1: Check if CSV export works
print("\n1. Testing CSV Export (Solution 1 - Manual)...")
try:
    from shopify_csv_export import ShopifyCSVExporter
    
    # Check if we have data files
    import glob
    csv_files = glob.glob('data/*.csv')
    
    if csv_files:
        print(f"   ✓ Found {len(csv_files)} data files")
        print(f"   ✓ CSV export ready")
        print(f"   → You can run: python shopify_csv_export.py 20")
        csv_export_works = True
    else:
        print("   ⚠ No data files found in data/ folder")
        print("   → Run scrapers first")
        csv_export_works = False
        
except Exception as e:
    print(f"   ✗ CSV export error: {e}")
    csv_export_works = False

# Test 2: Check if Selenium automation works
print("\n2. Testing Selenium Automation (Solution 2 - Automated)...")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    print("   ✓ Selenium installed")
    
    # Try to initialize Chrome driver
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("   ✓ Chrome driver working")
        selenium_works = True
    except Exception as e:
        print(f"   ⚠ Chrome driver issue: {e}")
        print("   → You may need to install Chrome driver")
        selenium_works = False
        
except Exception as e:
    print(f"   ✗ Selenium error: {e}")
    selenium_works = False

# Test 3: Check if Google Drive upload works
print("\n3. Testing Google Drive Upload (Solution 3 - Matrixify)...")
try:
    from upload_to_drive import GoogleDriveUploader
    
    if os.path.exists('credentials/credentials.json'):
        print("   ✓ Google credentials found")
        
        # Try to connect
        try:
            uploader = GoogleDriveUploader()
            if uploader.service:
                print("   ✓ Google Drive connection working")
                drive_works = True
            else:
                print("   ⚠ Could not connect to Google Drive")
                drive_works = False
        except Exception as e:
            print(f"   ⚠ Connection error: {e}")
            drive_works = False
    else:
        print("   ⚠ No Google credentials found")
        print("   → Need credentials/credentials.json")
        drive_works = False
        
except Exception as e:
    print(f"   ✗ Google Drive error: {e}")
    drive_works = False

# Test 4: Check if Google Sheets sync works
print("\n4. Testing Google Sheets Sync...")
try:
    from google_sheets_helper import GoogleSheetsHelper
    from config import SHEET_IDS
    
    if SHEET_IDS:
        print(f"   ✓ Found {len(SHEET_IDS)} configured sheets")
        
        # Try to connect
        try:
            helper = GoogleSheetsHelper()
            print("   ✓ Google Sheets connection working")
            sheets_works = True
        except Exception as e:
            print(f"   ⚠ Connection error: {e}")
            sheets_works = False
    else:
        print("   ⚠ No sheets configured in config.py")
        sheets_works = False
        
except Exception as e:
    print(f"   ✗ Google Sheets error: {e}")
    sheets_works = False

# Summary and recommendations
print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)

if csv_export_works and selenium_works and sheets_works:
    print("\n✅ BEST OPTION: Full Automation with Selenium")
    print("\nSetup:")
    print("  1. Run: .\\setup_shopify_sync_task.ps1 -ShopifyEmail 'admin@tbbt.de' -ShopifyPassword 'yourpass'")
    print("  2. Done! It will run automatically every Sunday at 4 AM")
    print("\nTest manually:")
    print("  python shopify_sync_from_sheets.py admin@tbbt.de yourpass 20")
    
elif csv_export_works and drive_works:
    print("\n✅ RECOMMENDED: Google Drive + Matrixify App")
    print("\nSetup:")
    print("  1. Convert CSVs: python shopify_csv_export.py 20")
    print("  2. Upload to Drive: python upload_to_drive.py")
    print("  3. Install Matrixify app in Shopify ($30/month)")
    print("  4. Configure Matrixify to import from Drive URLs")
    
elif csv_export_works:
    print("\n✅ AVAILABLE: Manual CSV Import")
    print("\nSteps:")
    print("  1. Convert CSVs: python shopify_csv_export.py 20")
    print("  2. Go to Shopify Admin → Products → Import")
    print("  3. Upload files from shopify_imports/ folder")
    print("  4. Review and publish products")
    
else:
    print("\n⚠ SETUP NEEDED")
    print("\nPlease:")
    print("  1. Run your scrapers to generate data files")
    print("  2. Make sure Google Sheets credentials are set up")
    print("  3. Re-run this test")

print("\n" + "=" * 70)
print("\nFor detailed instructions, see:")
print("  - SHOPIFY_AUTOMATION_SOLUTION.md")
print("  - SHOPIFY_FINAL_SOLUTION.md")
print("=" * 70)
