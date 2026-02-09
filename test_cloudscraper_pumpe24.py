"""
Test cloudscraper with pumpe24.de
"""
import cloudscraper

print("Creating cloudscraper session...")
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)

print("\nTesting homepage...")
try:
    response = scraper.get("https://www.pumpe24.de", timeout=30)
    print(f"Status code: {response.status_code}")
    print(f"Response length: {len(response.text)}")
    print(f"\nFirst 500 characters:")
    print(response.text[:500])
    
    if "Cloudflare" in response.text or "blocked" in response.text.lower():
        print("\n❌ Still blocked by Cloudflare")
    else:
        print("\n✓ Successfully bypassed Cloudflare!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
