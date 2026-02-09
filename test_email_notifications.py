"""
Test Email Notification System
Run this to verify your email configuration works
"""
from email_notifier import EmailNotifier
from email_config import (
    SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAILS
)
from datetime import datetime


def test_email_configuration():
    """Test basic email configuration"""
    print("="*70)
    print("EMAIL NOTIFICATION SYSTEM - CONFIGURATION TEST")
    print("="*70)
    
    print("\nChecking configuration...")
    print(f"  SMTP Server: {SMTP_SERVER}")
    print(f"  SMTP Port: {SMTP_PORT}")
    print(f"  Sender Email: {SENDER_EMAIL}")
    print(f"  Sender Password: {'*' * len(SENDER_PASSWORD)}")
    print(f"  Recipients: {', '.join(RECIPIENT_EMAILS)}")
    
    # Check for placeholder values
    if "your-email" in SENDER_EMAIL or "example.com" in SENDER_EMAIL:
        print("\n❌ ERROR: Please update SENDER_EMAIL in email_config.py")
        return False
    
    if "your-app-password" in SENDER_PASSWORD or len(SENDER_PASSWORD) < 8:
        print("\n❌ ERROR: Please update SENDER_PASSWORD in email_config.py")
        return False
    
    if any("example.com" in email for email in RECIPIENT_EMAILS):
        print("\n❌ ERROR: Please update RECIPIENT_EMAILS in email_config.py")
        return False
    
    print("\n✓ Configuration looks good!")
    return True


def send_test_email():
    """Send a test email"""
    print("\n" + "="*70)
    print("SENDING TEST EMAIL")
    print("="*70)
    
    try:
        # Initialize notifier
        notifier = EmailNotifier(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD,
            recipient_emails=RECIPIENT_EMAILS
        )
        
        # Create test email content
        subject = "🧪 Test Email - Scraper Notification System"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .success {{ background-color: #d4edda; border: 1px solid #c3e6cb; 
                           padding: 15px; border-radius: 5px; color: #155724; }}
                .info {{ background-color: #d1ecf1; border: 1px solid #bee5eb; 
                        padding: 15px; border-radius: 5px; color: #0c5460; margin-top: 20px; }}
                h1 {{ color: #2c3e50; }}
                ul {{ line-height: 1.8; }}
            </style>
        </head>
        <body>
            <h1>✅ Email Notification System Test</h1>
            
            <div class="success">
                <h2>Success!</h2>
                <p>If you're reading this, your email notification system is working correctly!</p>
            </div>
            
            <div class="info">
                <h3>Configuration Details:</h3>
                <ul>
                    <li><strong>SMTP Server:</strong> {SMTP_SERVER}</li>
                    <li><strong>SMTP Port:</strong> {SMTP_PORT}</li>
                    <li><strong>Sender:</strong> {SENDER_EMAIL}</li>
                    <li><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>What happens next?</h3>
                <p>When you run your scrapers with notifications enabled, you'll receive emails like this one 
                whenever there are changes detected:</p>
                <ul>
                    <li>🆕 New products added</li>
                    <li>🔄 Products updated (price changes, etc.)</li>
                    <li>❌ Products removed</li>
                </ul>
            </div>
            
            <p style="margin-top: 30px; color: #666;">
                <em>This is an automated test email from your scraper notification system.</em>
            </p>
        </body>
        </html>
        """
        
        # Send the email
        print("\nSending test email...")
        success = notifier.send_email(subject, html_content)
        
        if success:
            print("\n" + "="*70)
            print("✅ SUCCESS!")
            print("="*70)
            print("\nTest email sent successfully!")
            print(f"Check your inbox: {', '.join(RECIPIENT_EMAILS)}")
            print("\nIf you don't see it:")
            print("  1. Check your spam/junk folder")
            print("  2. Wait a few minutes (email can be delayed)")
            print("  3. Verify the recipient email address is correct")
            return True
        else:
            print("\n" + "="*70)
            print("❌ FAILED")
            print("="*70)
            print("\nFailed to send test email. Check the error message above.")
            return False
            
    except Exception as e:
        print("\n" + "="*70)
        print("❌ ERROR")
        print("="*70)
        print(f"\nAn error occurred: {e}")
        print("\nCommon issues:")
        print("  • Gmail: Make sure you're using an App Password, not your regular password")
        print("  • Outlook: Verify your password is correct")
        print("  • Firewall: Check if port 587 is blocked")
        print("  • SMTP Server: Verify the server address is correct")
        return False


def test_change_detection():
    """Test the change detection system"""
    print("\n" + "="*70)
    print("TESTING CHANGE DETECTION")
    print("="*70)
    
    from config import DATA_DIR
    import csv
    
    # Check if any CSV files exist
    csv_files = list(DATA_DIR.glob("*.csv"))
    
    if not csv_files:
        print("\n⚠ No CSV files found in data directory")
        print("Run a scraper first to test change detection")
        return False
    
    print(f"\nFound {len(csv_files)} CSV files")
    
    # Test with first CSV file
    test_csv = csv_files[0]
    scraper_name = test_csv.stem
    
    print(f"\nTesting with: {scraper_name}")
    
    try:
        notifier = EmailNotifier(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD,
            recipient_emails=RECIPIENT_EMAILS
        )
        
        # Detect changes
        new_products, updated_products, removed_products = notifier.detect_changes(
            scraper_name, str(test_csv)
        )
        
        print(f"\nResults:")
        print(f"  New products: {len(new_products)}")
        print(f"  Updated products: {len(updated_products)}")
        print(f"  Removed products: {len(removed_products)}")
        
        if len(new_products) + len(updated_products) + len(removed_products) == 0:
            print("\n✓ Change detection working (no changes on first run is normal)")
            print("  Run your scraper again tomorrow to see change detection in action")
        else:
            print("\n✓ Change detection working - changes detected!")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error testing change detection: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SCRAPER EMAIL NOTIFICATION SYSTEM - TEST SUITE")
    print("="*70)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Configuration
    print("\n\n📋 TEST 1: Configuration Check")
    config_ok = test_email_configuration()
    
    if not config_ok:
        print("\n" + "="*70)
        print("❌ TESTS FAILED")
        print("="*70)
        print("\nPlease fix the configuration errors in email_config.py and try again.")
        return
    
    # Test 2: Send test email
    print("\n\n📧 TEST 2: Send Test Email")
    email_ok = send_test_email()
    
    # Test 3: Change detection
    print("\n\n🔍 TEST 3: Change Detection")
    detection_ok = test_change_detection()
    
    # Summary
    print("\n\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Email Sending: {'✅ PASS' if email_ok else '❌ FAIL'}")
    print(f"Change Detection: {'✅ PASS' if detection_ok else '❌ FAIL'}")
    
    if config_ok and email_ok:
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        print("\nYour email notification system is ready to use!")
        print("\nNext steps:")
        print("  1. Run: python run_scrapers_with_notifications.py")
        print("  2. Schedule it to run daily (see EMAIL_NOTIFICATIONS_SETUP.md)")
        print("  3. Check your email for notifications!")
    else:
        print("\n" + "="*70)
        print("⚠ SOME TESTS FAILED")
        print("="*70)
        print("\nPlease review the errors above and fix them.")
        print("See EMAIL_NOTIFICATIONS_SETUP.md for help.")


if __name__ == "__main__":
    main()
