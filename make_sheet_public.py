"""
Make the Google Sheet public so Power BI can access it
"""
from google_sheets_helper import GoogleSheetsHelper

POWER_BI_SHEET_ID = "1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA"

helper = GoogleSheetsHelper()
spreadsheet = helper.client.open_by_key(POWER_BI_SHEET_ID)

print(f"Sheet: {spreadsheet.title}")
print(f"URL: {spreadsheet.url}")

# Share with anyone who has the link
try:
    spreadsheet.share(None, perm_type='anyone', role='reader')
    print("\n✓ Sheet is now public (anyone with link can view)")
    print("\nPower BI can now access:")
    print(f"  CSV URL: https://docs.google.com/spreadsheets/d/{POWER_BI_SHEET_ID}/export?format=csv")
except Exception as e:
    print(f"\n✗ Error making sheet public: {e}")
    print("\nPlease manually share the sheet:")
    print("1. Open the sheet in your browser")
    print("2. Click 'Share' button")
    print("3. Change to 'Anyone with the link' → 'Viewer'")
    print("4. Click 'Done'")
