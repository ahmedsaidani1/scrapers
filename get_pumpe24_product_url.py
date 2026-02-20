"""Get a real product URL from pumpe24"""
from pumpe24_scraper import Pumpe24Scraper
from bs4 import BeautifulSoup

scraper = Pumpe24Scraper()

# Get a category page
category_url = "https://www.pumpe24.de/pumpen/gartenpumpen.html"
print(f"Fetching category: {category_url}\n")

response = scraper.make_request(category_url)
if response:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find product links
    product_links = soup.select('a.product-item-link')
    
    print(f"Found {len(product_links)} product links\n")
    
    # Get first 5 product URLs
    for i, link in enumerate(product_links[:5], 1):
        href = link.get('href', '')
        name = link.get_text(strip=True)
        print(f"{i}. {name}")
        print(f"   URL: {href}\n")
else:
    print("Failed to fetch category page")
