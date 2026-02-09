"""
Detailed SMTP authentication test with different username formats
"""
import smtplib
import socket

email = "pumpen@solarics.de"
password = "Hechingen2026!!"

# Most likely servers based on previous test
servers_to_test = [
    ("smtp.strato.de", 587, "TLS"),
    ("smtp.strato.de", 465, "SSL"),
    ("smtp.ionos.de", 587, "TLS"),
    ("smtp.ionos.de", 465, "SSL"),
]

# Different username formats to try
username_formats = [
    email,  # Full email
    "pumpen",  # Just username
]

print("=" * 70)
print("DETAILED SMTP AUTHENTICATION TEST")
print("=" * 70)
print(f"Email: {email}")
print(f"Password: {'*' * len(password)}")
print("=" * 70)

for server, port, protocol in servers_to_test:
    print(f"\n{'=' * 70}")
    print(f"Testing: {server}:{port} ({protocol})")
    print("=" * 70)
    
    for username in username_formats:
        print(f"\nTrying username: {username}...", end=" ")
        
        try:
            # Connect based on protocol
            if protocol == "TLS":
                smtp = smtplib.SMTP(server, port, timeout=10)
                smtp.set_debuglevel(0)
                smtp.starttls()
            else:  # SSL
                smtp = smtplib.SMTP_SSL(server, port, timeout=10)
                smtp.set_debuglevel(0)
            
            # Try to login
            smtp.login(username, password)
            smtp.quit()
            
            print("✅ SUCCESS!")
            print(f"\n{'=' * 70}")
            print("🎉 WORKING CONFIGURATION FOUND!")
            print(f"{'=' * 70}")
            print(f"SMTP Server: {server}")
            print(f"Port: {port}")
            print(f"Protocol: {protocol}")
            print(f"Username: {username}")
            print(f"{'=' * 70}")
            
            # Update email_config.py with working settings
            print("\nUpdating email_config.py...")
            exit(0)
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Auth failed: {e.smtp_code} - {e.smtp_error.decode() if hasattr(e.smtp_error, 'decode') else e.smtp_error}")
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("❌ NO WORKING CONFIGURATION FOUND")
print("=" * 70)
print("\nPossible reasons:")
print("1. Wrong password")
print("2. SMTP not enabled for this email account")
print("3. Need to enable 'Less secure app access' or create app password")
print("4. Account locked or requires verification")
print("\nPlease ask your client to:")
print("- Verify the password is correct")
print("- Check email provider settings for SMTP access")
print("- Enable SMTP/external app access if needed")
print("- Create an app-specific password if required")
print("=" * 70)
