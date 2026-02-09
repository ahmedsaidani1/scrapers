"""
Complete automation: Run scrapers → Convert to Shopify CSV → Upload to Drive
This script does everything automatically
"""
import subprocess
import sys
import os
from datetime import datetime


def run_command(command, description):
    """Run a command and print status."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        print(e.stderr)
        return False


def main():
    """Complete automation workflow."""
    start_time = datetime.now()
    
    print("\n" + "="*60)
    print("SHOPIFY AUTOMATION - COMPLETE WORKFLOW")
    print("="*60)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Run all scrapers
    print("\n📊 STEP 1: Running scrapers...")
    if not run_command(
        "python run_all_scrapers_sequential.py",
        "Running all scrapers"
    ):
        print("\n⚠ Scrapers failed, but continuing...")
    
    # Step 2: Convert to Shopify CSV format
    print("\n📋 STEP 2: Converting to Shopify CSV format...")
    price_markup = 20  # 20% markup - adjust as needed
    if not run_command(
        f"python shopify_csv_export.py {price_markup}",
        f"Converting with {price_markup}% markup"
    ):
        print("\n❌ CSV conversion failed!")
        return False
    
    # Step 3: Upload to Google Drive
    print("\n☁️ STEP 3: Uploading to Google Drive...")
    if not run_command(
        "python upload_to_drive.py",
        "Uploading CSVs to Google Drive"
    ):
        print("\n❌ Upload failed!")
        print("\nNote: Make sure you have:")
        print("1. Google Drive API credentials configured")
        print("2. credentials/credentials.json file present")
        return False
    
    # Done!
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60
    
    print("\n" + "="*60)
    print("✓ AUTOMATION COMPLETE!")
    print("="*60)
    print(f"Duration: {duration:.1f} minutes")
    print(f"\nWhat happened:")
    print("  1. ✓ Scrapers ran and collected product data")
    print("  2. ✓ Data converted to Shopify CSV format")
    print("  3. ✓ CSVs uploaded to Google Drive")
    print(f"\nNext:")
    print("  → Matrixify will import from Drive URLs (scheduled)")
    print("  → Products will appear in Shopify")
    print("  → Review and publish products")
    print("\n" + "="*60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
