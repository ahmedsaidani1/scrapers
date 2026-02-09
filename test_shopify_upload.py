"""
SAFE TEST - Upload only 1 small file (5 products) to Shopify
This is for testing only - won't mess with your shop
"""
import sys
from shopify_selenium_uploader import ShopifySeleniumUploader


def main():
    print("=" * 70)
    print("SHOPIFY UPLOAD TEST - SAFE MODE")
    print("=" * 70)
    print("\nThis will upload ONLY 1 file with 5 products")
    print("Products will be imported as DRAFTS (not published)")
    print("You can review and delete them after testing")
    print("=" * 70)
    
    # Credentials
    email = "info@tbbt.de"
    password = "awyeff"
    
    # Initialize uploader
    uploader = ShopifySeleniumUploader(email, password)
    
    try:
        # Setup browser (not headless so you can watch)
        print("\nStarting Chrome browser...")
        uploader.setup_driver(headless=False)
        
        # Login
        print("\nLogging into Shopify...")
        if not uploader.login():
            print("\n❌ Login failed!")
            return
        
        print("\n✓ Login successful!")
        
        # Upload only the smallest file (wasserpumpe - 5 products)
        test_file = "shopify_imports/wasserpumpe_shopify.csv"
        
        print(f"\nUploading test file: {test_file}")
        print("This file has only 5 products")
        print("They will be imported as DRAFTS\n")
        
        if uploader.upload_csv(test_file):
            print("\n" + "=" * 70)
            print("✓ TEST SUCCESSFUL!")
            print("=" * 70)
            print("\nWhat happened:")
            print("  - 5 products uploaded to Shopify")
            print("  - All products are in DRAFT status")
            print("  - They are NOT published to your store")
            print("  - You can review them in Shopify admin")
            print("\nTo check:")
            print("  1. Go to Shopify admin → Products")
            print("  2. Filter by 'Draft' status")
            print("  3. You'll see the 5 test products")
            print("  4. Delete them if you want")
            print("\nTo run full automation:")
            print("  python shopify_sync_from_sheets.py info@tbbt.de awyeff 20")
        else:
            print("\n❌ Upload failed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nBrowser will stay open for 30 seconds so you can see what happened...")
        import time
        time.sleep(30)
        uploader.close()


if __name__ == "__main__":
    main()
