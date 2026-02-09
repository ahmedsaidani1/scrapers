"""
Push data to the new sheet with proper formatting
"""
from pathlib import Path
from google_sheets_helper import GoogleSheetsHelper

NEW_SHEET_ID = "15SdkCMxfZvD8SdHk0LveoGQFUY4zY0okQvuMUjcmyaU"
csv_file = Path("data/power_bi_test.csv")

print("Pushing to new sheet...")
helper = GoogleSheetsHelper()
result = helper.push_csv_to_sheet(NEW_SHEET_ID, csv_file)

if result:
    print("\nSuccess! Data pushed to new sheet")
    print(f"\nSheet URL: https://docs.google.com/spreadsheets/d/{NEW_SHEET_ID}")
    print(f"CSV Export: https://docs.google.com/spreadsheets/d/{NEW_SHEET_ID}/export?format=csv")
    
    # Verify
    spreadsheet = helper.client.open_by_key(NEW_SHEET_ID)
    worksheet = spreadsheet.sheet1
    values = worksheet.get_all_values()
    
    print(f"\nVerification:")
    print(f"  Total rows: {len(values)}")
    print(f"  Row 1 (headers): {values[0][:5]}")
    if len(values) > 1:
        print(f"  Row 2 (data): {values[1][:5]}")
else:
    print("Failed to push data")
