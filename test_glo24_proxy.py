"""
Test script to verify glo24.de proxy/VPN setup
"""
import cloudscraper
from config import SCRAPER_CONFIGS

def test_without_proxy():
    """Test accessing glo24.de without proxy (will likely fail)"""
    print("=" * 60)
    print("TEST 1: Accessing glo24.de WITHOUT proxy")
    print("=" * 60)
    
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    
    try:
        response = scraper.get('https://glo24.de', timeout=10)
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Success! Site is accessible without proxy")
        print(f"  Response length: {len(response.text)} bytes")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        print(f"  This is expected if you're not in Germany")
        return False

def test_with_proxy():
    """Test accessing glo24.de with configured proxy"""
    print("\n" + "=" * 60)
    print("TEST 2: Accessing glo24.de WITH proxy")
    print("=" * 60)
    
    config = SCRAPER_CONFIGS.get('glo24', {})
    proxy = config.get('proxy')
    
    if not proxy:
        print("✗ No proxy configured in config.py")
        print("  Please set 'proxy' in SCRAPER_CONFIGS['glo24']")
        return False
    
    print(f"Using proxy: {proxy}")
    
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    
    scraper.proxies = {
        'http': proxy,
        'https': proxy
    }
    
    try:
        response = scraper.get('https://glo24.de', timeout=30)
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Success! Site is accessible with proxy")
        print(f"  Response length: {len(response.text)} bytes")
        
        # Check if we got actual content
        if 'glo24' in response.text.lower() or len(response.text) > 1000:
            print(f"✓ Content looks valid")
            return True
        else:
            print(f"⚠ Warning: Response might be blocked/error page")
            return False
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        print(f"  Check proxy credentials and connection")
        return False

def test_proxy_location():
    """Test proxy IP location"""
    print("\n" + "=" * 60)
    print("TEST 3: Checking proxy IP location")
    print("=" * 60)
    
    config = SCRAPER_CONFIGS.get('glo24', {})
    proxy = config.get('proxy')
    
    if not proxy:
        print("✗ No proxy configured")
        return False
    
    scraper = cloudscraper.create_scraper()
    scraper.proxies = {
        'http': proxy,
        'https': proxy
    }
    
    try:
        # Check IP location
        response = scraper.get('https://ipapi.co/json/', timeout=10)
        data = response.json()
        
        print(f"Proxy IP: {data.get('ip', 'Unknown')}")
        print(f"Country: {data.get('country_name', 'Unknown')} ({data.get('country_code', 'Unknown')})")
        print(f"City: {data.get('city', 'Unknown')}")
        print(f"Region: {data.get('region', 'Unknown')}")
        
        if data.get('country_code') == 'DE':
            print(f"✓ Proxy is in Germany - Perfect!")
            return True
        else:
            print(f"⚠ Warning: Proxy is NOT in Germany")
            print(f"  glo24.de requires German IP")
            return False
            
    except Exception as e:
        print(f"✗ Failed to check location: {e}")
        return False

def test_sitemap_access():
    """Test accessing glo24.de sitemap"""
    print("\n" + "=" * 60)
    print("TEST 4: Accessing glo24.de sitemap")
    print("=" * 60)
    
    config = SCRAPER_CONFIGS.get('glo24', {})
    proxy = config.get('proxy')
    
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    
    if proxy:
        scraper.proxies = {
            'http': proxy,
            'https': proxy
        }
        print(f"Using proxy: {proxy}")
    else:
        print("No proxy configured - testing without proxy")
    
    try:
        response = scraper.get('https://glo24.de/sitemap.xml', timeout=30)
        print(f"✓ Status Code: {response.status_code}")
        
        if 'xml' in response.text[:100].lower():
            print(f"✓ Sitemap is accessible")
            print(f"  Response length: {len(response.text)} bytes")
            
            # Count URLs in sitemap
            url_count = response.text.count('<loc>')
            print(f"  Found ~{url_count} URLs in sitemap")
            return True
        else:
            print(f"⚠ Warning: Response doesn't look like XML")
            return False
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("GLO24.DE PROXY/VPN TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Without proxy
    results.append(("Without Proxy", test_without_proxy()))
    
    # Test 2: With proxy
    results.append(("With Proxy", test_with_proxy()))
    
    # Test 3: Proxy location
    results.append(("Proxy Location", test_proxy_location()))
    
    # Test 4: Sitemap access
    results.append(("Sitemap Access", test_sitemap_access()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed >= 3:
        print("\n✓ Setup looks good! You can run the scraper now.")
    elif passed >= 2:
        print("\n⚠ Partial success. Check warnings above.")
    else:
        print("\n✗ Setup needs attention. See errors above.")
        print("\nQuick fixes:")
        print("1. Make sure proxy is configured in config.py")
        print("2. Verify proxy credentials are correct")
        print("3. Ensure proxy is a German IP address")
        print("4. Try a different proxy service if current one fails")

if __name__ == "__main__":
    main()
