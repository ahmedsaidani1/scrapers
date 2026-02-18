"""
Find actual product items on the page
"""
from bs4 import BeautifulSoup

with open('pumpenheizung_page_test.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("Looking for product items...")

# The page likely has a list/grid of products
# Look for repeating structures with product info

# Check for article tags
articles = soup.select('article')
print(f"\nArticle tags: {len(articles)}")
if articles:
    first = articles[0]
    print(f"  First article classes: {first.get('class', [])}")
    print(f"  Has link: {bool(first.select_one('a[href]'))}")
    if first.select_one('a[href]'):
        print(f"  Link: {first.select_one('a[href]').get('href')}")

# Check for divs with specific classes
product_divs = soup.select('div[class*="artikel"], div[class*="produkt"]')
print(f"\nDivs with 'artikel' or 'produkt': {len(product_divs)}")

# Look for price indicators
prices = soup.select('[class*="preis"], [class*="price"]')
print(f"\nPrice elements: {len(prices)}")
if prices:
    print(f"  Sample: {prices[0].get_text(strip=True)[:50]}")

# Look for "add to cart" buttons
cart_buttons = soup.select('button[class*="cart"], a[class*="cart"], input[value*="Warenkorb"]')
print(f"\nCart buttons: {len(cart_buttons)}")

# Check the main content area
main_content = soup.select('main, #main, .main-content, #content')
print(f"\nMain content areas: {len(main_content)}")

if main_content:
    # Look for links within main content that go to product pages
    links_in_main = main_content[0].select('a[href]')
    print(f"  Links in main: {len(links_in_main)}")
    
    # Filter for product-like URLs (deeper paths)
    product_like = [
        a.get('href') for a in links_in_main 
        if a.get('href') and a.get('href').count('/') >= 2 and 'pumpen-heizung.de' in a.get('href', '')
    ]
    print(f"  Product-like links (>=2 slashes): {len(set(product_like))}")
    
    if product_like:
        print(f"\n  Sample product URLs:")
        for url in list(set(product_like))[:10]:
            print(f"    {url}")
