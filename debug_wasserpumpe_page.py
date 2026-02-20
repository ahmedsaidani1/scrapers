"""
Debug wasserpumpe page structure to understand price and article number extraction
"""
from wasserpumpe_scraper import WasserpumpeScraper
from bs4 import BeautifulSoup
import json


def main():
    scraper = WasserpumpeScraper()
    
    # Test with a real product URL from the category
    test_url = "https://wasserpumpe.de/dab-divertron-900-m-tauchdruckpumpe#specifications"
    
    print(f"Fetching: {test_url}")
    response = scraper.make_request(test_url, attempts=3, timeout=35)
    
    if not response:
        print("Failed to fetch page")
        return
    
    soup = scraper.parse_html(response.text)
    
    # Save HTML for inspection
    with open("wasserpumpe_debug_page.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved HTML to wasserpumpe_debug_page.html")
    
    # Check JSON-LD
    print("\n" + "="*60)
    print("JSON-LD DATA")
    print("="*60)
    scripts = soup.find_all("script", {"type": "application/ld+json"})
    for i, script in enumerate(scripts, 1):
        raw = script.string or script.get_text(strip=True)
        if raw:
            try:
                data = json.loads(raw)
                print(f"\nJSON-LD #{i}:")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
            except:
                print(f"\nJSON-LD #{i}: Failed to parse")
    
    # Check price selectors
    print("\n" + "="*60)
    print("PRICE EXTRACTION")
    print("="*60)
    
    price_selectors = [
        "span.price",
        "span[itemprop='price']",
        "div.product-info-price span.price",
        "meta[itemprop='price']",
        "div.price",
        "[data-price]",
    ]
    
    for selector in price_selectors:
        elements = soup.select(selector)
        if elements:
            print(f"\n{selector}:")
            for elem in elements[:3]:
                if elem.name == "meta":
                    print(f"  content: {elem.get('content')}")
                else:
                    print(f"  text: {elem.get_text(strip=True)}")
                    if elem.get('data-price'):
                        print(f"  data-price: {elem.get('data-price')}")
    
    # Check article number selectors
    print("\n" + "="*60)
    print("ARTICLE NUMBER EXTRACTION")
    print("="*60)
    
    sku_selectors = [
        "div.product-info-stock-sku div.value",
        "span[itemprop='sku']",
        "div.product-sku",
        "meta[itemprop='sku']",
        "[itemprop='sku']",
        "td:contains('Item number')",
        "td:contains('sku')",
    ]
    
    for selector in sku_selectors:
        elements = soup.select(selector)
        if elements:
            print(f"\n{selector}:")
            for elem in elements[:3]:
                if elem.name == "meta":
                    print(f"  content: {elem.get('content')}")
                else:
                    print(f"  text: {elem.get_text(strip=True)}")
    
    # Search for "Item number" in text
    print("\n\nSearching for 'Item number' in page text...")
    if "Item number" in response.text:
        import re
        matches = re.findall(r'Item number[:\s]+[{(]?sku[)}]?[:\s]+(\d+)', response.text, re.IGNORECASE)
        if matches:
            print(f"Found: {matches}")
    
    # Search for price patterns
    print("\n\nSearching for price patterns in page text...")
    import re
    price_patterns = [
        r'"price":\s*"?(\d+\.?\d*)"?',
        r'"price":\s*(\d+\.?\d*)',
        r'data-price="([^"]+)"',
        r'€\s*(\d+[.,]\d{2})',
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, response.text)
        if matches:
            print(f"\nPattern {pattern}:")
            print(f"  Found: {matches[:5]}")
    
    print("\n" + "="*60)
    print("CURRENT SCRAPER OUTPUT")
    print("="*60)
    product = scraper.scrape_product(test_url)
    if product:
        for key, value in product.items():
            print(f"{key:20s}: {value}")
    else:
        print("Failed to scrape product")


if __name__ == "__main__":
    main()
