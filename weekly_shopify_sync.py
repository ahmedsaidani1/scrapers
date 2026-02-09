"""
Complete weekly automation: Convert CSVs + Upload to Shopify
Run this after your scrapers finish.
"""
import subprocess
import sys
import os

def main():
    if len(sys.argv) < 3:
        print("Usage: python weekly_shopify_sync.py <email> <password> [markup%]")
        print("\nExample:")
        print("  python weekly_shopify_sync.py admin@tbbt.de mypassword 20")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    markup = sys.argv[3] if len(sys.argv) > 3 else "20"
    
    print("=" * 70)
    print("WEEKLY SHOPIFY SYNC")
    print("=" * 70)
    
    # Step 1: Convert CSVs
    print("\nSTEP 1: Converting data to Shopify CSV format...")
    print("-" * 70)
    result = subprocess.run(["python", "shopify_csv_export.py", markup])
    
    if result.returncode != 0:
        print("\n❌ CSV conversion failed!")
        sys.exit(1)
    
    print("\n✓ CSV conversion complete")
    
    # Step 2: Upload to Shopify
    print("\n" + "=" * 70)
    print("STEP 2: Uploading to Shopify...")
    print("-" * 70)
    result = subprocess.run(["python", "auto_shopify_upload.py", email, password])
    
    if result.returncode != 0:
        print("\n❌ Upload failed!")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✓ WEEKLY SYNC COMPLETE!")
    print("=" * 70)
    print("\nProducts uploaded to Shopify as drafts.")
    print("Review them in Shopify Admin before publishing.")

if __name__ == "__main__":
    main()
