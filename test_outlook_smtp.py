"""
Test Outlook/Microsoft 365 SMTP servers
"""
import smtplib

email = "pumpen@solarics.de"
password = "Hechingen2026!!"

# Outlook/Microsoft 365 SMTP servers
servers_to_test = [
    ("smtp-mail.outlook.com", 587, "TLS"),
    ("smtp.office365.com", 587, "TLS"),
]

print("=" * 70)
print("TESTING OUTLOOK/MICROSOFT 365 SMTP")
print("=" * 70)
print(f"Email: {email}")
print(f"Password: {'*' * len(password)}")
print("=" * 70)

for server, port, protocol in servers_to_test:
    print(f"\nTesting {server}:{port} ({protocol})...", end=" ")
    
    try:
        smtp = smtplib.SMTP(server, port, timeout=10)
        smtp.set_debuglevel(0)
        smtp.starttls()
        
        # Try to login
        smtp.login(email, password)
        smtp.quit()
        
        print("✅ SUCCESS!")
        print(f"\n{'=' * 70}")
        print("🎉 WORKING CONFIGURATION FOUND!")
        print(f"{'=' * 70}")
        print(f"SMTP Server: {server}")
        print(f"Port: {port}")
        print(f"Protocol: {protocol}")
        print(f"Username: {email}")
        print(f"{'=' * 70}")
        exit(0)
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = e.smtp_error.decode() if hasattr(e.smtp_error, 'decode') else str(e.smtp_error)
        print(f"❌ Auth failed: {e.smtp_code} - {error_msg}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("❌ AUTHENTICATION FAILED")
print("=" * 70)
print("\nFor Outlook/Microsoft 365, you may need to:")
print("1. Enable 'SMTP AUTH' in Microsoft 365 admin center")
print("2. Use an App Password instead of regular password:")
print("   - Go to: https://account.microsoft.com/security")
print("   - Click 'Advanced security options'")
print("   - Under 'App passwords', create a new one")
print("   - Use that password instead")
print("3. Check if 2FA is enabled (requires app password)")
print("4. Verify the password is correct")
print("=" * 70)
