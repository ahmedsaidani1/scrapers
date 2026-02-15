"""
Advanced test for pumpen-heizung.de with different approaches
"""
import requests
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

print("Advanced testing for pumpen-heizung.de...")
print("=" * 60)

# Test 1: With custom headers
print("\n1. Testing with custom headers...")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    response = requests.get("https://pumpen-heizung.de", headers=headers, timeout=15)
    print(f"   ✓ Status: {response.status_code}")
    print(f"   ✓ Response time: {response.elapsed.total_seconds():.2f}s")
except Exception as e:
    print(f"   ✗ Failed: {type(e).__name__}: {str(e)[:100]}")

# Test 2: Try HTTP instead of HTTPS
print("\n2. Testing HTTP (non-secure)...")
try:
    response = requests.get("http://pumpen-heizung.de", timeout=15)
    print(f"   ✓ Status: {response.status_code}")
    print(f"   ✓ URL: {response.url}")
except Exception as e:
    print(f"   ✗ Failed: {type(e).__name__}: {str(e)[:100]}")

# Test 3: Check DNS resolution
print("\n3. Testing DNS resolution...")
try:
    import socket
    ip = socket.gethostbyname("pumpen-heizung.de")
    print(f"   ✓ IP Address: {ip}")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 4: Selenium (headless Chrome)
print("\n4. Testing with Selenium (headless Chrome)...")
try:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(20)
    
    start = time.time()
    driver.get("https://pumpen-heizung.de")
    elapsed = time.time() - start
    
    print(f"   ✓ Page loaded in {elapsed:.2f}s")
    print(f"   ✓ Title: {driver.title}")
    print(f"   ✓ URL: {driver.current_url}")
    
    # Save page source
    with open("pumpenheizung_selenium.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source[:5000])
    print("   ✓ Saved HTML to pumpenheizung_selenium.html")
    
    driver.quit()
    
except Exception as e:
    print(f"   ✗ Failed: {type(e).__name__}: {str(e)[:100]}")
    try:
        driver.quit()
    except:
        pass

print("\n" + "=" * 60)
print("Advanced test complete!")
