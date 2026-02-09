"""
Test Google Sheets push for wolfonlineshop
"""
from google_sheets_helper import GoogleSheetsHelper
from pathlib import Path
import traceback

sheet_id = "1IR3BAObUJf4cUxdX9OF1zka0YsOrP35c-n8F4xIl3a8"
csv_file = Path("data/wolfonlineshop.csv")

print(f"Sheet ID: {sheet_id}")
print(f"CSV file: {csv_file}")
print(f"CSV exists: {csv_file.exists()}")

try:
    helper = GoogleSheetsHelper()
    print("✓ Authentication successful")
    
    result = helper.push_csv_to_sheet(sheet_id, csv_file)
    
    if result:
        print("✓ Successfully pushed to Google Sheets!")
    else:
        print("✗ Failed to push to Google Sheets")
        
except Exception as e:
    print(f"✗ Error: {e}")
    traceback.print_exc()
