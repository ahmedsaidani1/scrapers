"""Save wolf-online-shop HTML for analysis"""
import cloudscraper

scraper = cloudscraper.create_scraper()
response = scraper.get('https://www.wolf-online-shop.de')

with open('wolf_homepage.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print(f"Saved {len(response.text)} bytes to wolf_homepage.html")

# Also save a product page if we can find one
from bs4 import BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Look for any link with product info
links = soup.find_all('a', href=True)
for link in links:
    href = link.get('href')
    if 'product' in href.lower() and '=' in href:
        print(f"\nFound product link: {href}")
        
        if href.startswith('/'):
            full_url = 'https://www.wolf-online-shop.de' + href
        elif not href.startswith('http'):
            full_url = 'https://www.wolf-online-shop.de/' + href
        else:
            full_url = href
        
        print(f"Fetching: {full_url}")
        prod_response = scraper.get(full_url)
        
        with open('wolf_product.html', 'w', encoding='utf-8') as f:
            f.write(prod_response.text)
        
        print(f"Saved product page to wolf_product.html")
        break
