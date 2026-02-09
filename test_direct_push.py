"""
Test direct push to Google Sheets with detailed logging
"""
from pathlib import Path
from google_sheets_helper import GoogleSheetsHelper
import traceback

POWER_BI_SHEET_ID = "1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA"
csv_file = Path("data/power_bi_test.csv")

print("Testing direct push to Google Sheets...")
print(f"CSV file: {csv_file}")
print(f"CSV exists: {csv_file.exists()}")

if csv_file.exists():
    # Check CSV content
    with open(csv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"CSV has {len(lines)} lines")
        print(f"First line (header): {lines[0][:100]}...")
        if len(lines) > 1:
            print(f"Second line (data): {lines[1][:100]}...")

try:
    helper = GoogleSheetsHelper()
    print("\nAuthenticated successfully")
    
    # Try to push
    print(f"\nPushing to sheet {POWER_BI_SHEET_ID}...")
    result = helper.push_csv_to_sheet(POWER_BI_SHEET_ID, csv_file)
    
    if result:
        print("Push successful!")
    else:
        print("Push failed!")
        
except Exception as e:
    print(f"\nError: {e}")
    traceback.print_exc()
