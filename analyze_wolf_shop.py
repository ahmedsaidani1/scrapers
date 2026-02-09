"""Analyze wolf-online-shop structure"""
import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()

print("Fetching homepage...")
response = scraper.get('https://www.wolf-online-shop.de')

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links
    links = soup.find_all('a', href=True)
    
    print(f"\nTotal links found: {len(links)}")
    
    # Categorize links
    product_links = []
    category_links = []
    
    for link in links:
        href = link.get('href')
        text = link.get_text(strip=True)
        
        if 'product_info.php' in href or 'products_id=' in href:
            product_links.append((href, text))
        elif 'index.php?cPath=' in href:
            category_links.append((href, text))
    
    print(f"\nProduct links found: {len(product_links)}")
    if product_links:
        print("\nFirst 10 product links:")
        for i, (href, text) in enumerate(product_links[:10], 1):
            print(f"{i}. {href[:80]}... | {text[:50]}")
    
    print(f"\nCategory links found: {len(category_links)}")
    if category_links:
        print("\nFirst 10 category links:")
        for i, (href, text) in enumerate(category_links[:10], 1):
            print(f"{i}. {href[:80]}... | {text[:50]}")
    
    # Look for Art.Nr patterns
    print("\n\nSearching for Art.Nr. patterns...")
    art_nr_elements = soup.find_all(string=lambda text: text and 'Art.Nr.' in text)
    print(f"Found {len(art_nr_elements)} elements with Art.Nr.")
    
    if art_nr_elements:
        print("\nFirst 5 Art.Nr. contexts:")
        for i, elem in enumerate(art_nr_elements[:5], 1):
            print(f"{i}. {str(elem)[:100]}")
            if elem.parent:
                print(f"   Parent: {elem.parent.name}")
                if elem.parent.find_parent('a'):
                    link = elem.parent.find_parent('a')
                    print(f"   Link: {link.get('href', 'N/A')}")
    
else:
    print(f"Failed: {response.status_code}")
