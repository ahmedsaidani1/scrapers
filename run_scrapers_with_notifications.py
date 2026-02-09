"""
Run all scrapers and send email notifications for changes
This script should be run daily via scheduled task
"""
import sys
from pathlib import Path
from datetime import datetime
from email_notifier import EmailNotifier
from email_config import (
    SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD,
    RECIPIENT_EMAILS, MONITORED_SCRAPERS, SEND_ONLY_ON_CHANGES,
    MIN_CHANGES_THRESHOLD
)
from config import DATA_DIR

# Import all scrapers
from meinhausshop_scraper import MeinhausshopScraper
from heima24_scraper import Heima24Scraper
from sanundo_scraper import SanundoScraper
from heizungsdiscount24_scraper import Heizungsdiscount24Scraper
from wolfonlineshop_scraper import WolfonlineshopScraper
from st_shop24_scraper import StShop24Scraper
from selfio_scraper import SelfioScraper
from pumpe24_scraper import Pumpe24Scraper
from wasserpumpe_scraper import WasserpumpeScraper
from glo24_scraper import Glo24Scraper


# Map scraper names to classes
SCRAPER_CLASSES = {
    "meinhausshop": MeinhausshopScraper,
    "heima24": Heima24Scraper,
    "sanundo": SanundoScraper,
    "heizungsdiscount24": Heizungsdiscount24Scraper,
    "wolfonlineshop": WolfonlineshopScraper,
    "st_shop24": StShop24Scraper,
    "selfio": SelfioScraper,
    "pumpe24": Pumpe24Scraper,
    "wasserpumpe": WasserpumpeScraper,
    "glo24": Glo24Scraper,
}


def run_scraper(scraper_name: str, scraper_class) -> bool:
    """Run a single scraper"""
    print(f"\n{'='*70}")
    print(f"Running {scraper_name.upper()} scraper...")
    print(f"{'='*70}")
    
    try:
        scraper = scraper_class()
        success_count = scraper.run()
        
        print(f"\n✓ {scraper_name}: Scraped {success_count} products")
        return True
        
    except Exception as e:
        print(f"\n✗ {scraper_name}: Error - {e}")
        return False


def main():
    """Main execution"""
    start_time = datetime.now()
    
    print("="*70)
    print("SCRAPER AUTOMATION WITH EMAIL NOTIFICATIONS")
    print("="*70)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Monitoring {len(MONITORED_SCRAPERS)} scrapers")
    print("="*70)
    
    # Initialize email notifier
    try:
        notifier = EmailNotifier(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD,
            recipient_emails=RECIPIENT_EMAILS
        )
        print("✓ Email notifier initialized")
    except Exception as e:
        print(f"✗ Failed to initialize email notifier: {e}")
        print("Continuing without email notifications...")
        notifier = None
    
    # Run scrapers
    results = {}
    
    for scraper_name in MONITORED_SCRAPERS:
        if scraper_name not in SCRAPER_CLASSES:
            print(f"\n⚠ Warning: Scraper '{scraper_name}' not found, skipping...")
            continue
        
        scraper_class = SCRAPER_CLASSES[scraper_name]
        success = run_scraper(scraper_name, scraper_class)
        results[scraper_name] = success
    
    # Check for changes and send notifications
    if notifier:
        print("\n" + "="*70)
        print("CHECKING FOR CHANGES AND SENDING NOTIFICATIONS")
        print("="*70)
        
        total_notifications = 0
        
        for scraper_name in MONITORED_SCRAPERS:
            if not results.get(scraper_name, False):
                print(f"\n⚠ Skipping {scraper_name} (scraping failed)")
                continue
            
            csv_path = DATA_DIR / f"{scraper_name}.csv"
            
            if csv_path.exists():
                try:
                    # Detect changes
                    new_products, updated_products, removed_products = notifier.detect_changes(
                        scraper_name, str(csv_path)
                    )
                    
                    total_changes = len(new_products) + len(updated_products) + len(removed_products)
                    
                    print(f"\n{scraper_name}:")
                    print(f"  New: {len(new_products)}")
                    print(f"  Updated: {len(updated_products)}")
                    print(f"  Removed: {len(removed_products)}")
                    
                    # Send notification if threshold met
                    if total_changes >= MIN_CHANGES_THRESHOLD:
                        subject = f"🔔 {scraper_name.upper()} - {total_changes} Changes Detected"
                        html_content = notifier.format_html_email(
                            scraper_name, new_products, updated_products, removed_products
                        )
                        
                        if notifier.send_email(subject, html_content):
                            total_notifications += 1
                    else:
                        print(f"  No email sent (below threshold of {MIN_CHANGES_THRESHOLD})")
                
                except Exception as e:
                    print(f"  ✗ Error checking changes: {e}")
            else:
                print(f"\n⚠ {scraper_name}: CSV file not found")
        
        print(f"\n{'='*70}")
        print(f"Sent {total_notifications} email notifications")
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*70)
    print("EXECUTION SUMMARY")
    print("="*70)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration}")
    print(f"\nResults:")
    
    for scraper_name, success in results.items():
        status = "✓ Success" if success else "✗ Failed"
        print(f"  {scraper_name}: {status}")
    
    successful = sum(1 for s in results.values() if s)
    print(f"\nTotal: {successful}/{len(results)} scrapers successful")
    print("="*70)


if __name__ == "__main__":
    main()
