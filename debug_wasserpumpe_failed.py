"""
Debug the 2 products that failed to get proper prices
"""
from wasserpumpe_scraper import WasserpumpeScraper
from bs4 import BeautifulSoup
import json


def debug_product(scraper, url):
    print("\n" + "="*60)
    print(f"Debugging: {url}")
    print("="*60)
    
    response = scraper.make_request(url, attempts=3, timeout=35)
    if not response:
        print("Failed to fetch page")
        return
    
    soup = scraper.parse_html(response.text)
    
    # Check JSON-LD
    print("\nJSON-LD Product Data:")
    scripts = soup.find_all("script", {"type": "application/ld+json"})
    found_product = False
    
    for script in scripts:
        raw = script.string or script.get_text(strip=True)
        if not raw:
            continue
        
        try:
            data = json.loads(raw)
            candidates = []
            if isinstance(data, dict):
                candidates.append(data)
                graph = data.get("@graph")
                if isinstance(graph, list):
                    candidates.extend(item for item in graph if isinstance(item, dict))
            elif isinstance(data, list):
                candidates.extend(item for item in data if isinstance(item, dict))
            
            for item in candidates:
                type_value = item.get("@type", "")
                if isinstance(type_value, list):
                    is_product = any(str(t).lower() == "product" for t in type_value)
                else:
                    is_product = str(type_value).lower() == "product"
                
                if is_product:
                    found_product = True
                    print(f"  Name: {item.get('name')}")
                    print(f"  SKU: {item.get('sku')}")
                    
                    brand = item.get('brand')
                    if isinstance(brand, dict):
                        print(f"  Brand: {brand.get('name')}")
                    else:
                        print(f"  Brand: {brand}")
                    
                    offers = item.get('offers')
                    if isinstance(offers, list) and offers:
                        offers = offers[0]
                    if isinstance(offers, dict):
                        print(f"  Price: {offers.get('price')}")
                        print(f"  Currency: {offers.get('priceCurrency')}")
                    else:
                        print(f"  Offers: {offers}")
        except Exception as e:
            continue
    
    if not found_product:
        print("  No Product JSON-LD found!")
    
    # Check what the scraper returns
    print("\nScraper Output:")
    product = scraper.scrape_product(url)
    if product:
        for key, value in product.items():
            print(f"  {key}: {value}")
    else:
        print("  Failed to scrape")


def main():
    scraper = WasserpumpeScraper()
    
    # The 2 products that failed
    failed_urls = [
        "https://www.wasserpumpe.de/dab-evosta-2-umwaelzpumpe",
        "https://www.wasserpumpe.de/grundfos-alpha-2"
    ]
    
    for url in failed_urls:
        debug_product(scraper, url)


if __name__ == "__main__":
    main()
