"""Test different techniques to bypass 403 errors"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sites_403 = [
    "https://pumpe24.de",
    "https://wasserpumpe.de", 
    "https://glo24.de"
]

# Different user agents to try
user_agents = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # Googlebot (sometimes works)
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
]

for site in sites_403:
    print(f"\n{'='*70}")
    print(f"Testing: {site}")
    print('='*70)
    
    # Test 1: Different User Agents
    print("\n1. Testing different User Agents:")
    for i, ua in enumerate(user_agents, 1):
        try:
            headers = {
                'User-Agent': ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            r = requests.get(site, headers=headers, timeout=10, allow_redirects=True)
            print(f"   UA {i}: Status {r.status_code} - {ua[:50]}...")
            if r.status_code == 200:
                print(f"   ✓ SUCCESS with this User Agent!")
                break
        except Exception as e:
            print(f"   UA {i}: Error - {str(e)[:50]}")
    
    # Test 2: With Session and Cookies
    print("\n2. Testing with Session:")
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': user_agents[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9',
            'Referer': 'https://www.google.com/',
        })
        r = session.get(site, timeout=10)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print(f"   ✓ SUCCESS with Session!")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Check if sitemap is accessible
    print("\n3. Testing sitemap access:")
    try:
        sitemap_url = f"{site}/sitemap.xml"
        r = requests.get(sitemap_url, headers={'User-Agent': user_agents[0]}, timeout=10)
        print(f"   Sitemap status: {r.status_code}")
        if r.status_code == 200:
            print(f"   ✓ Sitemap is accessible!")
    except Exception as e:
        print(f"   Sitemap error: {e}")
    
    # Test 4: Check robots.txt
    print("\n4. Checking robots.txt:")
    try:
        robots_url = f"{site}/robots.txt"
        r = requests.get(robots_url, headers={'User-Agent': user_agents[0]}, timeout=10)
        print(f"   Robots.txt status: {r.status_code}")
        if r.status_code == 200:
            print(f"   Content preview: {r.text[:200]}")
    except Exception as e:
        print(f"   Robots.txt error: {e}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
