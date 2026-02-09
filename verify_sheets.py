"""Verify Google Sheets data"""
from google_sheets_helper import GoogleSheetsHelper

helper = GoogleSheetsHelper()
sheet = helper.client.open_by_key('1IR3BAObUJf4cUxdX9OF1zka0YsOrP35c-n8F4xIl3a8')
ws = sheet.sheet1

values = ws.get_all_values()
print(f"Sheet title: {sheet.title}")
print(f"Total rows with data: {len(values)}")
print(f"Product count (excluding header): {len(values) - 1}")

if len(values) > 0:
    print(f"\nHeader row: {values[0]}")
    
if len(values) > 1:
    print(f"\nFirst product:")
    for i, col in enumerate(values[0]):
        print(f"  {col}: {values[1][i]}")
