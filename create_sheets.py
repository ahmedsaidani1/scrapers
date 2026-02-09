"""
Script to create Google Sheets for scrapers.
Run this once to set up your sheets automatically.
"""
from google_sheets_helper import GoogleSheetsHelper
from config import CSV_COLUMNS

def create_sheets():
    """Create Google Sheets for each scraper."""
    
    # Initialize helper
    helper = GoogleSheetsHelper()
    
    # Define scrapers
    scrapers = [
        {
            "name": "Akusolar (No Login)",
            "scraper_id": "akusolar"
        },
        {
            "name": "Priwatt (With Login)",
            "scraper_id": "priwatt"
        }
    ]
    
    print("="*60)
    print("Creating Google Sheets for Scrapers")
    print("="*60)
    print()
    
    sheet_ids = {}
    
    for scraper in scrapers:
        name = scraper["name"]
        scraper_id = scraper["scraper_id"]
        
        print(f"Creating sheet: {name}...")
        
        try:
            # Create the sheet
            sheet_id = helper.create_new_sheet(
                title=f"Solar Scraper - {name}",
                share_with_email=None  # Already has service account access
            )
            
            if sheet_id:
                sheet_ids[scraper_id] = sheet_id
                print(f"✓ Created: {name}")
                print(f"  Sheet ID: {sheet_id}")
                print(f"  URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
                print()
            else:
                print(f"✗ Failed to create: {name}")
                print()
                
        except Exception as e:
            print(f"✗ Error creating {name}: {e}")
            print()
    
    # Print summary
    print("="*60)
    print("Summary")
    print("="*60)
    print()
    print("Add these to config.py SHEET_IDS:")
    print()
    print("SHEET_IDS = {")
    for scraper_id, sheet_id in sheet_ids.items():
        print(f'    "{scraper_id}": "{sheet_id}",')
    print("}")
    print()
    print("="*60)
    print(f"Created {len(sheet_ids)} sheets successfully!")
    print("="*60)

if __name__ == "__main__":
    create_sheets()
