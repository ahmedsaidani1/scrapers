"""
Complete weekly automation - NO SHOPIFY CREDENTIALS NEEDED
1. Converts scraped data to Shopify CSV
2. Uploads to Google Drive
3. Client's Matrixify app auto-imports from Drive
"""
import subprocess
import sys

def main():
    markup = sys.argv[1] if len(sys.argv) > 1 else "20"
    
    print("=" * 70)
    print("WEEKLY SHOPIFY AUTO-SYNC")
    print("=" * 70)
    print("\nThis automation requires NO Shopify credentials!")
    print("Your client will use Matrixify app to auto-import.")
    
    # Step 1: Convert to Shopify CSV
    print("\n" + "=" * 70)
    print("STEP 1: Converting to Shopify CSV format")
    print("=" * 70)
    
    result = subprocess.run(["python", "shopify_csv_export.py", markup])
    if result.returncode != 0:
        print("\n❌ CSV conversion failed!")
        sys.exit(1)
    
    # Step 2: Upload to Google Drive
    print("\n" + "=" * 70)
    print("STEP 2: Uploading to Google Drive")
    print("=" * 70)
    
    result = subprocess.run(["python", "auto_upload_to_drive.py"])
    if result.returncode != 0:
        print("\n❌ Upload to Drive failed!")
        sys.exit(1)
    
    # Done
    print("\n" + "=" * 70)
    print("✓ WEEKLY SYNC COMPLETE!")
    print("=" * 70)
    print("\nFiles uploaded to Google Drive.")
    print("Matrixify will auto-import them on schedule.")
    print("\nCheck: shopify_imports/MATRIXIFY_URLS.txt")

if __name__ == "__main__":
    main()
