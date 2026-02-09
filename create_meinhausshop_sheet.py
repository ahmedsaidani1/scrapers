"""
Create Google Sheet for MeinHausShop scraper
"""
from google_sheets_helper import GoogleSheetsHelper

def create_sheet():
    """Create a new Google Sheet for MeinHausShop data."""
    
    print("Creating Google Sheet for MeinHausShop...")
    print("="*60)
    
    helper = GoogleSheetsHelper()
    
    # Create new sheet
    sheet_title = "MeinHausShop - Product Data"
    
    # Share with service account email
    service_email = "webscraping-solarics@webscrapingmajd2.iam.gserviceaccount.com"
    
    sheet_id = helper.create_new_sheet(
        title=sheet_title,
        share_with_email=service_email
    )
    
    if sheet_id:
        print(f"\n✓ Successfully created Google Sheet!")
        print(f"\nSheet ID: {sheet_id}")
        print(f"Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
        print(f"\n{'='*60}")
        print(f"IMPORTANT: Add this Sheet ID to config.py:")
        print(f"  'meinhausshop': '{sheet_id}',")
        print(f"{'='*60}")
        
        return sheet_id
    else:
        print("\n✗ Failed to create Google Sheet")
        return None


if __name__ == "__main__":
    create_sheet()
