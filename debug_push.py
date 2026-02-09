"""
Debug the push issue
"""
import csv
from pathlib import Path
from google_sheets_helper import GoogleSheetsHelper

NEW_SHEET_ID = "15SdkCMxfZvD8SdHk0LveoGQFUY4zY0okQvuMUjcmyaU"
csv_file = Path("data/power_bi_test.csv")

# Read CSV
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    data = list(reader)

print(f"CSV has {len(data)} rows")
print(f"First row: {data[0]}")
print(f"Second row: {data[1][:5]}")

# Connect
helper = GoogleSheetsHelper()
spreadsheet = helper.client.open_by_key(NEW_SHEET_ID)
worksheet = spreadsheet.sheet1

print(f"\nConnected to: {spreadsheet.title}")

# Clear
worksheet.clear()
print("Cleared sheet")

# Update using the correct method
print("\nUpdating sheet...")
try:
    # Use the correct argument order for gspread v5+
    result = worksheet.update(values=data, range_name='A1', value_input_option='USER_ENTERED')
    print(f"Update result: {result}")
    
    # Verify immediately
    import time
    time.sleep(2)  # Wait for Google to process
    
    values = worksheet.get_all_values()
    print(f"\nVerification:")
    print(f"  Rows in sheet: {len(values)}")
    if values:
        print(f"  First row: {values[0][:5]}")
        if len(values) > 1:
            print(f"  Second row: {values[1][:5]}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
