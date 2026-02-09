"""
Test script to check what's actually in the Google Sheet
"""
from google_sheets_helper import GoogleSheetsHelper

POWER_BI_SHEET_ID = "1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA"

helper = GoogleSheetsHelper()

# Open the spreadsheet
spreadsheet = helper.client.open_by_key(POWER_BI_SHEET_ID)
worksheet = spreadsheet.sheet1

# Get first 5 rows to see the structure
data = worksheet.get_all_values()

print("First 5 rows from Google Sheet:")
print("=" * 80)
for i, row in enumerate(data[:5], 1):
    print(f"Row {i}: {row[:5]}...")  # Show first 5 columns
    
print("\n" + "=" * 80)
print(f"Total rows: {len(data)}")
print(f"Total columns: {len(data[0]) if data else 0}")

# Check data types in row 2 (first data row)
if len(data) > 1:
    print("\nRow 2 values and types:")
    for i, val in enumerate(data[1][:11]):  # First 11 columns
        print(f"  Column {i+1} ({data[0][i]}): '{val}' (type: {type(val).__name__})")
