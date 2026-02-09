"""
Test pushing MeinHausShop data to Google Sheets
"""
from google_sheets_helper import push_data
from config import SHEET_IDS
from pathlib import Path

def test_push():
    """Test pushing CSV data to Google Sheets."""
    
    sheet_id = SHEET_IDS.get("meinhausshop")
    csv_file = Path("data/meinhausshop.csv")
    
    print("="*60)
    print("TESTING GOOGLE SHEETS PUSH")
    print("="*60)
    print(f"\nSheet ID: {sheet_id}")
    print(f"CSV File: {csv_file}")
    print(f"Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
    
    if not csv_file.exists():
        print("\n✗ CSV file not found!")
        print("Run test_meinhausshop_batch.py first to generate test data")
        return False
    
    print(f"\nPushing data to Google Sheets...")
    
    try:
        success = push_data(sheet_id, csv_file)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    if success:
        print("\n✓ Successfully pushed data to Google Sheets!")
        print(f"\nView your data here:")
        print(f"https://docs.google.com/spreadsheets/d/{sheet_id}")
    else:
        print("\n✗ Failed to push data to Google Sheets")
    
    print("\n" + "="*60)
    
    return success


if __name__ == "__main__":
    test_push()
