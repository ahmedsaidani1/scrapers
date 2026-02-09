"""Quick test to check wolf-online-shop sitemap structure"""
import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()

print("Fetching sitemap...")
response = scraper.get('https://www.wolf-online-shop.de/sitemap.xml')

if response.status_code == 200:
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    print("\nFirst 2000 characters:")
    print(response.text[:2000])
    
    soup = BeautifulSoup(response.text, 'xml')
    urls = soup.find_all('loc')
    print(f"\nTotal URLs found: {len(urls)}")
    
    if urls:
        print("\nFirst 10 URLs:")
        for i, url in enumerate(urls[:10], 1):
            print(f"{i}. {url.text}")
else:
    print(f"Failed: {response.status_code}")
