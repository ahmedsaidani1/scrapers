"""
Check what's actually in the Google Sheet
"""
from google_sheets_helper import GoogleSheetsHelper

POWER_BI_SHEET_ID = "1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA"

helper = GoogleSheetsHelper()
spreadsheet = helper.client.open_by_key(POWER_BI_SHEET_ID)
worksheet = spreadsheet.sheet1

# Get all values
all_values = worksheet.get_all_values()

print(f"Total rows in sheet: {len(all_values)}")
print("\nFirst 3 rows:")
print("=" * 100)

for i, row in enumerate(all_values[:3], 1):
    print(f"\nRow {i}:")
    for j, cell in enumerate(row[:11], 1):  # First 11 columns
        print(f"  Col {j}: '{cell}'")

# Check if row 1 has headers
if all_values:
    print("\n" + "=" * 100)
    print("Row 1 (should be headers):")
    print(all_values[0])
    
    if len(all_values) > 1:
        print("\nRow 2 (first data row):")
        print(all_values[1][:11])  # First 11 columns
        
        # Check data types in Google Sheets
        print("\n" + "=" * 100)
        print("Checking price columns in Google Sheets:")
        
        # Find price columns
        headers = all_values[0]
        price_net_idx = headers.index('price_net') if 'price_net' in headers else None
        price_gross_idx = headers.index('price_gross') if 'price_gross' in headers else None
        
        if price_net_idx and len(all_values) > 1:
            print(f"price_net (col {price_net_idx+1}): '{all_values[1][price_net_idx]}'")
            print(f"  Type in Python: {type(all_values[1][price_net_idx])}")
            
        if price_gross_idx and len(all_values) > 1:
            print(f"price_gross (col {price_gross_idx+1}): '{all_values[1][price_gross_idx]}'")
            print(f"  Type in Python: {type(all_values[1][price_gross_idx])}")
