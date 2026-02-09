"""
Send a test email with actual scraped products
"""
from email_notifier import EmailNotifier
from email_config import (
    SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD,
    RECIPIENT_EMAILS
)
from config import DATA_DIR
from pathlib import Path

def main():
    print("="*70)
    print("SENDING TEST EMAIL WITH REAL PRODUCTS")
    print("="*70)
    
    # Initialize email notifier
    notifier = EmailNotifier(
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        sender_email=SENDER_EMAIL,
        sender_password=SENDER_PASSWORD,
        recipient_emails=RECIPIENT_EMAILS
    )
    
    print(f"\nSender: {SENDER_EMAIL}")
    print(f"Recipients: {', '.join(RECIPIENT_EMAILS)}")
    
    # Pick a scraper with data (heima24 is fast and has good data)
    scraper_name = "heima24"
    csv_path = DATA_DIR / f"{scraper_name}.csv"
    
    if not csv_path.exists():
        print(f"\n❌ No data found for {scraper_name}")
        print("Run the scraper first: python run_heima24_50.py")
        return
    
    print(f"\nUsing data from: {scraper_name}")
    print(f"CSV file: {csv_path}")
    
    # Load the CSV data
    current_data = notifier.load_csv_data(str(csv_path))
    
    print(f"Found {len(current_data)} products")
    
    # Take first 20 products as "new" for demo
    products_list = list(current_data.values())[:20]
    
    print(f"\nCreating email with {len(products_list)} sample products...")
    
    # Create email with these products as "new"
    html_content = notifier.format_html_email(
        scraper_name=scraper_name,
        new_products=products_list,
        updated_products=[],
        removed_products=[]
    )
    
    # Send email
    subject = f"🔔 TEST: {scraper_name.upper()} - {len(products_list)} Sample Products"
    
    print(f"\nSending email...")
    print(f"Subject: {subject}")
    
    if notifier.send_email(subject, html_content):
        print("\n" + "="*70)
        print("✅ SUCCESS!")
        print("="*70)
        print(f"\nTest email sent to: {', '.join(RECIPIENT_EMAILS)}")
        print("\nCheck your inbox at: pumpen@solarics.de")
        print("\nThe email contains:")
        print(f"  • {len(products_list)} sample products")
        print("  • Product names, manufacturers, categories")
        print("  • Prices and direct links")
        print("  • Formatted HTML tables with styling")
        print("="*70)
    else:
        print("\n❌ Failed to send email")
        print("Check the error message above")

if __name__ == "__main__":
    main()
