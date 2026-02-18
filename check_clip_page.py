"""
Check if Clip page is a category with products or a single product
"""
import requests
from bs4 import BeautifulSoup

url = "https://pumpen-heizung.de/Clip"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

# Count links in main content
main = soup.select_one('main, #main')
if main:
    all_links = main.select('a[href]')
    product_links = [
        a.get('href') for a in all_links 
        if a.get('href') and a.get('href').count('/') >= 2 and 'pumpen-heizung.de' in a.get('href', '')
    ]
    
    print(f"Links in main: {len(all_links)}")
    print(f"Product-like links: {len(set(product_links))}")
    
    if product_links:
        print(f"\nSample product links:")
        for link in list(set(product_links))[:10]:
            print(f"  {link}")
    
    # Check if this is a listing page
    print(f"\nIs this a category/listing page? {len(set(product_links)) > 10}")
