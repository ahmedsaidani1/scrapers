"""Test scraping a specific wolf-online-shop product to debug field extraction"""
import cloudscraper
from bs4 import BeautifulSoup

# The product from the screenshot
url = "https://www.wolf-online-shop.de/GARDENA-Schneewanne-Arbeitsbreite-700mm-Teleskopstange-200685::526582.html"

scraper = cloudscraper.create_scraper()
response = scraper.get(url)

print(f"Status: {response.status_code}")
print(f"URL: {url}")
print("=" * 80)

soup = BeautifulSoup(response.text, 'html.parser')

# Save HTML for inspection
with open('wolf_product_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print("HTML saved to wolf_product_page.html")
print("=" * 80)

# Try to find manufacturer
print("\nSearching for manufacturer...")
print("-" * 80)

# Look for text containing "Manufacturer"
manufacturer_text = soup.find_all(string=lambda text: text and 'Manufacturer' in text)
print(f"Found {len(manufacturer_text)} elements with 'Manufacturer'")
for i, text in enumerate(manufacturer_text[:5], 1):
    print(f"{i}. {text}")
    if text.parent:
        print(f"   Parent: {text.parent.name}")
        # Get next sibling or nearby text
        next_elem = text.parent.find_next()
        if next_elem:
            print(f"   Next: {next_elem.get_text(strip=True)[:100]}")

print("\n" + "=" * 80)
print("Searching for 'GARDENA'...")
print("-" * 80)

gardena_text = soup.find_all(string=lambda text: text and 'GARDENA' in text)
print(f"Found {len(gardena_text)} elements with 'GARDENA'")
for i, text in enumerate(gardena_text[:5], 1):
    print(f"{i}. {text.strip()}")
    if text.parent:
        print(f"   Parent: {text.parent.name}, class: {text.parent.get('class')}")

print("\n" + "=" * 80)
print("Looking for structured data...")
print("-" * 80)

# Look for table or definition list
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

dls = soup.find_all('dl')
print(f"Found {len(dls)} definition lists")

# Look for specific patterns
print("\nSearching for 'Article No' or 'Art.Nr.'...")
art_nr = soup.find_all(string=lambda text: text and ('Article No' in text or 'Art.Nr.' in text or 'HAN:' in text))
for i, text in enumerate(art_nr[:3], 1):
    print(f"{i}. {text.strip()}")
    if text.parent:
        print(f"   Parent: {text.parent.name}")
        next_text = text.parent.find_next()
        if next_text:
            print(f"   Next: {next_text.get_text(strip=True)[:100]}")
