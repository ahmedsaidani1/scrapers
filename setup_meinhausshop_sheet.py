"""
Setup script for MeinHausShop Google Sheet
This script helps you set up the Google Sheet manually
"""

print("="*70)
print("GOOGLE SHEET SETUP FOR MEINHAUSSHOP")
print("="*70)

print("\nSTEP 1: Create a new Google Sheet")
print("-" * 70)
print("1. Go to: https://sheets.google.com")
print("2. Click '+ Blank' to create a new spreadsheet")
print("3. Name it: 'MeinHausShop - Product Data'")

print("\n\nSTEP 2: Share the sheet with the service account")
print("-" * 70)
print("1. Click the 'Share' button (top right)")
print("2. Add this email address:")
print("   webscraping-solarics@webscrapingmajd2.iam.gserviceaccount.com")
print("3. Give it 'Editor' permissions")
print("4. Click 'Send' (uncheck 'Notify people')")

print("\n\nSTEP 3: Get the Sheet ID")
print("-" * 70)
print("1. Look at the URL of your Google Sheet")
print("2. The URL looks like:")
print("   https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit")
print("3. Copy the SHEET_ID_HERE part")

print("\n\nSTEP 4: Update config.py")
print("-" * 70)
print("1. Open config.py")
print("2. Find the SHEET_IDS section")
print("3. Replace this line:")
print("   'meinhausshop': 'TBD',")
print("4. With:")
print("   'meinhausshop': 'YOUR_SHEET_ID_HERE',")

print("\n\nSTEP 5: Test the connection")
print("-" * 70)
print("Run this command to test:")
print("   python test_sheets_meinhausshop.py")

print("\n" + "="*70)
print("After completing these steps, you can push data to Google Sheets!")
print("="*70)

# Ask user for sheet ID
print("\n\nIf you've already created the sheet, enter the Sheet ID now:")
print("(or press Enter to skip)")
sheet_id = input("Sheet ID: ").strip()

if sheet_id:
    print(f"\n✓ Sheet ID received: {sheet_id}")
    print(f"\nAdd this to config.py:")
    print(f"  'meinhausshop': '{sheet_id}',")
    
    # Update config.py automatically
    try:
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the TBD with actual sheet ID
        updated_content = content.replace(
            '"meinhausshop": "TBD"',
            f'"meinhausshop": "{sheet_id}"'
        )
        
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("\n✓ config.py updated successfully!")
        
    except Exception as e:
        print(f"\n✗ Failed to update config.py: {e}")
        print("Please update it manually.")
else:
    print("\nNo Sheet ID provided. Follow the steps above to set up manually.")
