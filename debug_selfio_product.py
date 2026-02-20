"""
Debug selfio product page to understand structure
"""
from selfio_scraper import SelfioScraper


def main():
    scraper = SelfioScraper()
    
    # Get first product URL
    urls = scraper.get_product_urls(max_sitemaps=1)
    if not urls:
        print("No URLs found!")
        return
    
    test_url = urls[0]
    print(f"Testing URL: {test_url}\n")
    
    response = scraper.make_request(test_url)
    if not response:
        print("Failed to fetch page")
        return
    
    soup = scraper.parse_html(response.text)
    
    # Save HTML for inspection
    with open("selfio_debug_page.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved HTML to selfio_debug_page.html\n")
    
    # Check what the scraper extracts
    print("="*60)
    print("SCRAPER OUTPUT")
    print("="*60)
    product = scraper.scrape_product(test_url)
    if product:
        for key, value in product.items():
            print(f"{key:20s}: {value}")
    else:
        print("Failed to scrape product")
    
    # Check for price elements
    print("\n" + "="*60)
    print("PRICE ELEMENTS")
    print("="*60)
    
    price_selectors = [
        'meta[itemprop="price"]',
        'span.product-detail-price',
        'div.product-price .price',
        'span[itemprop="price"]',
        'span.price',
        '[data-price]',
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


if __name__ == "__main__":
    main()
