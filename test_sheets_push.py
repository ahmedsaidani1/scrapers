"""Test pushing data to Google Sheets"""
from google_sheets_helper import push_data
from config import SHEET_IDS
from pathlib import Path

# Test Priwatt sheet
sheet_id = SHEET_IDS.get("priwatt")
csv_file = Path("data/priwatt.csv")

print(f"Sheet ID: {sheet_id}")
print(f"CSV file: {csv_file}")
print(f"CSV exists: {csv_file.exists()}")

if csv_file.exists():
    print(f"\nPushing data to Google Sheets...")
    result = push_data(sheet_id, csv_file)
    
    if result:
        print("✓ Successfully pushed to Google Sheets!")
        print(f"\nView your data at:")
        print(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
    else:
        print("✗ Failed to push to Google Sheets")
else:
    print("✗ CSV file not found")
