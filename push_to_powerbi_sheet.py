"""
Push the scraped Power BI test data to Google Sheets
"""
from pathlib import Path
from google_sheets_helper import push_data

# Google Sheet ID for Power BI testing
POWER_BI_SHEET_ID = "1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg"

# CSV file with all scraped products
csv_file = Path("data/power_bi_test.csv")

if not csv_file.exists():
    print(f"✗ CSV file not found: {csv_file}")
    print("Run 'python run_power_bi_test.py' first to scrape the data")
    exit(1)

print("=" * 80)
print("PUSHING DATA TO GOOGLE SHEETS")
print("=" * 80)
print(f"Sheet ID: {POWER_BI_SHEET_ID}")
print(f"CSV File: {csv_file}")
print()

try:
    push_data(
        sheet_id=POWER_BI_SHEET_ID,
        csv_file=csv_file
    )
    print("✓ Successfully pushed data to Google Sheets!")
    print()
    print("NEXT STEPS:")
    print("1. Open: https://docs.google.com/spreadsheets/d/" + POWER_BI_SHEET_ID)
    print("2. Verify the data is there")
    print("3. Open Power BI Desktop")
    print("4. Get Data → Web → Enter the Google Sheets URL")
    print("5. Follow POWER_BI_ARTICLE_SEARCH_GUIDE.md")
except Exception as e:
    print(f"✗ Failed to push to Google Sheets: {e}")
    print()
    print("TROUBLESHOOTING:")
    print("1. Share the Google Sheet with: webscraping-solarics@webscrapingmajd2.iam.gserviceaccount.com")
    print("2. Give it 'Editor' permissions")
    print("3. Run this script again")
    exit(1)
