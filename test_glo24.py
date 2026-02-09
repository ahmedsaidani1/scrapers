"""
Test glo24.de access
"""
import cloudscraper

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

print("Testing glo24.de homepage...")
try:
    response = scraper.get("https://glo24.de", timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Final URL: {response.url}")
    print(f"Content length: {len(response.text)}")
    print(f"\nFirst 1000 characters:")
    print(response.text[:1000])
    
    if "Cloudflare" in response.text or "blocked" in response.text.lower():
        print("\n❌ Still blocked by Cloudflare")
    else:
        print("\n✓ Successfully accessed!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n\nTesting sitemap...")
try:
    response = scraper.get("https://glo24.de/sitemap.xml", timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    print(f"\nFirst 500 characters:")
    print(response.text[:500])
except Exception as e:
    print(f"❌ Error: {e}")
