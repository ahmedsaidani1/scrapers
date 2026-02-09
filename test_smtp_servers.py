"""
Test different SMTP servers to find the correct one for solarics.de
"""
import smtplib
import socket

email = "pumpen@solarics.de"
password = "Hechingen2026!!"

# Common SMTP servers for German hosting providers
smtp_servers = [
    ("smtp.solarics.de", 587),
    ("smtp.solarics.de", 465),
    ("mail.solarics.de", 587),
    ("mail.solarics.de", 465),
    ("smtp.strato.de", 587),
    ("smtp.strato.de", 465),
    ("smtp.ionos.de", 587),
    ("smtp.ionos.de", 465),
    ("smtp.1und1.de", 587),
    ("smtp.1und1.de", 465),
    ("smtp.hosteurope.de", 587),
    ("smtp.hosteurope.de", 465),
    ("smtp.netcup.net", 587),
    ("smtp.netcup.net", 465),
]

print("=" * 70)
print("TESTING SMTP SERVERS FOR pumpen@solarics.de")
print("=" * 70)

for server, port in smtp_servers:
    print(f"\nTrying {server}:{port}...", end=" ")
    
    try:
        # First check if server exists
        socket.gethostbyname(server)
        
        # Try to connect
        if port == 587:
            smtp = smtplib.SMTP(server, port, timeout=10)
            smtp.starttls()
        else:  # 465
            smtp = smtplib.SMTP_SSL(server, port, timeout=10)
        
        # Try to login
        smtp.login(email, password)
        smtp.quit()
        
        print("✅ SUCCESS!")
        print(f"\n{'=' * 70}")
        print(f"FOUND WORKING SMTP SERVER:")
        print(f"Server: {server}")
        print(f"Port: {port}")
        print(f"{'=' * 70}")
        break
        
    except socket.gaierror:
        print("❌ Server not found")
    except smtplib.SMTPAuthenticationError:
        print("⚠️  Server exists but authentication failed (wrong password?)")
    except smtplib.SMTPException as e:
        print(f"⚠️  SMTP error: {e}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}")

print("\n" + "=" * 70)
print("Test complete!")
print("=" * 70)
