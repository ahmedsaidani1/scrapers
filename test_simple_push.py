"""
Simple test to push data directly
"""
import csv
from pathlib import Path
from google_sheets_helper import GoogleSheetsHelper

POWER_BI_SHEET_ID = "1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA"
csv_file = Path("data/power_bi_test.csv")

# Read CSV
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    data = list(reader)

print(f"Read {len(data)} rows from CSV")
print(f"First row: {data[0][:5]}")
print(f"Second row: {data[1][:5]}")

# Connect to Google Sheets
helper = GoogleSheetsHelper()
spreadsheet = helper.client.open_by_key(POWER_BI_SHEET_ID)
worksheet = spreadsheet.sheet1

print(f"\nConnected to sheet: {spreadsheet.title}")

# Clear the sheet
worksheet.clear()
print("Cleared sheet")

# Try simple update
print("\nAttempting to update...")
try:
    # Method 1: Update with range
    worksheet.update('A1', data, value_input_option='USER_ENTERED')
    print("Update successful!")
    
    # Verify
    values = worksheet.get_all_values()
    print(f"\nVerification: Sheet now has {len(values)} rows")
    if values:
        print(f"First row in sheet: {values[0][:5]}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
