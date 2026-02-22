"""
Test st_shop24 EAN and article number extraction from details table
"""
from st_shop24_scraper import StShop24Scraper

def test_details_extraction():
    scraper = StShop24Scraper()
    
    # Test with a real working URL
    test_url = "https://st-shop24.de/dichtungen/grundfos-kit-gleitringdichtung-fur-ch-v-2-4-auue-auuv-985848.html"
    
    print(f"Testing: {test_url}\n")
    
    product = scraper.scrape_product(test_url)
    
    if product:
        print(f"Name: {product.get('name', 'N/A')}")
        print(f"Manufacturer: {product.get('manufacturer', 'N/A')}")
        print(f"Article Number: {product.get('article_number', 'N/A')}")
        print(f"EAN: {product.get('ean', 'N/A')}")
        print(f"Price: {product.get('price_gross', 'N/A')}")
        print(f"Image: {product.get('product_image', 'N/A')[:80]}")
        
        # Check if we got values
        if product.get('ean'):
            print(f"\n✓ EAN extracted: {product.get('ean')}")
        else:
            print(f"\n✗ EAN missing!")
        
        if product.get('article_number'):
            print(f"✓ Article number extracted: {product.get('article_number')}")
        else:
            print(f"✗ Article number missing!")
    else:
        print("✗ Failed to scrape product")

if __name__ == "__main__":
    test_details_extraction()
