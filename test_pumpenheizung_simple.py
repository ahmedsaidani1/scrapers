"""
Simple test to check if pumpen-heizung.de is accessible
"""
import requests
import cloudscraper
import time

print("Testing pumpen-heizung.de accessibility...")
print("=" * 60)

# Test 1: Simple requests
print("\n1. Testing with requests library...")
try:
    response = requests.get("https://pumpen-heizung.de", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response time: {response.elapsed.total_seconds():.2f}s")
    print(f"   Content length: {len(response.text)} bytes")
except Exception as e:
    print(f"   Failed: {e}")

# Test 2: Cloudscraper
print("\n2. Testing with cloudscraper...")
try:
    scraper = cloudscraper.create_scraper()
    response = scraper.get("https://pumpen-heizung.de", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response time: {response.elapsed.total_seconds():.2f}s")
    print(f"   Content length: {len(response.text)} bytes")
    
    # Check what's in the response
    if "cloudflare" in response.text.lower():
        print("   ⚠️  Cloudflare detected")
    if "captcha" in response.text.lower():
        print("   ⚠️  CAPTCHA detected")
    
    # Save sample HTML
    with open("pumpenheizung_sample.html", "w", encoding="utf-8") as f:
        f.write(response.text[:5000])  # First 5000 chars
    print("   ✓ Saved sample HTML to pumpenheizung_sample.html")
    
except Exception as e:
    print(f"   Failed: {e}")

print("\n" + "=" * 60)
print("Test complete!")
