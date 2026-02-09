"""
Full automation: Scrape → Convert → Upload to Shopify
Runs weekly without human involvement.
"""
import os
import sys
import subprocess
import time
from datetime import datetime


def run_command(command, description):
    """Run a command and show progress."""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"{'='*70}")
    print(f"Command: {command}\n")
    
    result = subprocess.run(command, shell=True, capture_output=False)
    
    if result.returncode == 0:
        print(f"✓ {description} completed successfully")
        return True
    else:
        print(f"❌ {description} failed")
        return False


def main():
    """Run full automation pipeline."""
    start_time = datetime.now()
    
    print("=" * 70)
    print("FULL SHOPIFY AUTOMATION")
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Get credentials from environment or command line
    email = os.getenv('SHOPIFY_EMAIL') or (sys.argv[1] if len(sys.argv) > 1 else None)
    password = os.getenv('SHOPIFY_PASSWORD') or (sys.argv[2] if len(sys.argv) > 2 else None)
    
    if not email or not password:
        print("\n❌ Shopify credentials required!")
        print("\nOption 1: Set environment variables:")
        print("  set SHOPIFY_EMAIL=your@email.com")
        print("  set SHOPIFY_PASSWORD=yourpassword")
        print("\nOption 2: Pass as arguments:")
        print("  python run_full_automation.py your@email.com yourpassword")
        sys.exit(1)
    
    # Step 1: Run all scrapers
    if not run_command(
        "python run_all_scrapers_parallel.py",
        "Step 1: Running all scrapers"
    ):
        print("\n⚠ Scraping had some errors, but continuing...")
    
    # Step 2: Convert to Shopify format
    if not run_command(
        "python shopify_csv_export.py 20",  # 20% markup
        "Step 2: Converting to Shopify CSV format (20% markup)"
    ):
        print("\n❌ CSV conversion failed!")
        sys.exit(1)
    
    # Step 3: Upload to Shopify
    if not run_command(
        f'python shopify_selenium_uploader.py "{email}" "{password}"',
        "Step 3: Uploading to Shopify"
    ):
        print("\n❌ Shopify upload failed!")
        sys.exit(1)
    
    # Done
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 70)
    print("✓ FULL AUTOMATION COMPLETE!")
    print("=" * 70)
    print(f"Started:  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration}")
    print("=" * 70)
    
    # Send notification (optional)
    try:
        from email_notifier import EmailNotifier
        notifier = EmailNotifier()
        notifier.send_notification(
            subject="Shopify Automation Complete",
            message=f"Full automation completed successfully in {duration}"
        )
        print("✓ Email notification sent")
    except:
        pass


if __name__ == "__main__":
    main()
