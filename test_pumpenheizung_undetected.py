"""
Test pumpen-heizung.de with undetected-chromedriver
This bypasses most bot detection systems
"""
import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup

print("Testing pumpen-heizung.de with undetected-chromedriver...")
print("=" * 60)

try:
    # Create undetected Chrome driver
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')  # New headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    print("\n1. Initializing undetected Chrome...")
    driver = uc.Chrome(options=options, version_main=None)
    driver.set_page_load_timeout(30)
    
    print("2. Loading website...")
    start = time.time()
    driver.get("https://pumpen-heizung.de")
    elapsed = time.time() - start
    
    print(f"   ✓ Page loaded in {elapsed:.2f}s")
    print(f"   ✓ Title: {driver.title}")
    print(f"   ✓ URL: {driver.current_url}")
    
    # Wait for page to fully load
    time.sleep(3)
    
    # Get page source
    html = driver.page_source
    print(f"   ✓ HTML length: {len(html)} bytes")
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Look for products
    print("\n3. Looking for products...")
    
    # Try different selectors
    product_links = []
    selectors = [
        'a[href*="produkt"]',
        'a[href*="product"]',
        'a[href*="artikel"]',
        '.product a',
        '.item a',
        'a.product-link',
        'a.product-item-link'
    ]
    
    for selector in selectors:
        links = soup.select(selector)
        if links:
            print(f"   ✓ Found {len(links)} links with selector: {selector}")
            for link in links[:5]:  # Show first 5
                href = link.get('href', '')
                text = link.get_text(strip=True)[:50]
                print(f"      - {text}: {href[:80]}")
            product_links.extend(links)
            break
    
    if not product_links:
        print("   ⚠️  No product links found with standard selectors")
        print("   Checking all links...")
        all_links = soup.find_all('a', href=True)
        print(f"   Found {len(all_links)} total links")
        
        # Show first 20 links
        print("\n   First 20 links:")
        for i, link in enumerate(all_links[:20], 1):
            href = link.get('href', '')
            text = link.get_text(strip=True)[:40]
            print(f"   {i}. {text}: {href[:60]}")
    
    # Save HTML for analysis
    with open("pumpenheizung_undetected.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n4. ✓ Saved full HTML to pumpenheizung_undetected.html")
    
    # Check for categories
    print("\n5. Looking for navigation/categories...")
    nav_elements = soup.find_all(['nav', 'ul', 'div'], class_=lambda x: x and ('nav' in x.lower() or 'menu' in x.lower() or 'category' in x.lower()))
    print(f"   Found {len(nav_elements)} navigation elements")
    
    driver.quit()
    print("\n✓ Test successful!")
    
except Exception as e:
    print(f"\n✗ Failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    try:
        driver.quit()
    except:
        pass

print("\n" + "=" * 60)
print("Test complete!")
