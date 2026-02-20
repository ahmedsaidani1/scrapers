"""Debug pumpe24 product page"""
from pumpe24_scraper import Pumpe24Scraper

scraper = Pumpe24Scraper()

test_url = "https://www.pumpe24.de/pumpe-espa-aspri-15-5m-gg-0-95kw-verkabelt.html"
print(f"Testing URL: {test_url}\n")

response = scraper.make_request(test_url)
if not response:
    print("Failed to fetch page")
    exit()

soup = scraper.parse_html(response.text)

# Save HTML for inspection
with open("pumpe24_debug.html", "w", encoding="utf-8") as f:
    f.write(response.text)
print("Saved HTML to pumpe24_debug.html\n")

# Check for manufacturer elements
print("="*60)
print("MANUFACTURER ELEMENTS")
print("="*60)

manufacturer_selectors = [
    'a.product-manufacturer',
    'span[itemprop="brand"]',
    'div.product-brand',
    'meta[itemprop="brand"]',
    '[itemprop="brand"]',
    'div.product-attribute-manufacturer',
]

for selector in manufacturer_selectors:
    elements = soup.select(selector)
    if elements:
        print(f"\n{selector}:")
        for elem in elements[:3]:
            if elem.name == "meta":
                print(f"  content: {elem.get('content')}")
            else:
                print(f"  text: {elem.get_text(strip=True)}")

# Check for article number elements
print("\n" + "="*60)
print("ARTICLE NUMBER ELEMENTS")
print("="*60)

article_selectors = [
    'div.product-info-stock-sku div.value',
    'span[itemprop="sku"]',
    'div.product-sku',
    'meta[itemprop="sku"]',
    '[itemprop="sku"]',
    'div.product-attribute-sku',
]

for selector in article_selectors:
    elements = soup.select(selector)
    if elements:
        print(f"\n{selector}:")
        for elem in elements[:3]:
            if elem.name == "meta":
                print(f"  content: {elem.get('content')}")
            else:
                print(f"  text: {elem.get_text(strip=True)}")

# Check product name
print("\n" + "="*60)
print("PRODUCT NAME")
print("="*60)
product_name = scraper._extract_text(soup, [
    'h1.page-title span',
    'h1.product-name',
    'h1[itemprop="name"]',
    'h1'
])
print(f"Product name: {product_name}")
print(f"First word: {product_name.split()[0] if product_name else 'N/A'}")
