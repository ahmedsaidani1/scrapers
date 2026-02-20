"""Test pumpe24 with 5 more products"""
from pumpe24_scraper import Pumpe24Scraper
from bs4 import BeautifulSoup

scraper = Pumpe24Scraper()

# Get more product URLs
category_url = "https://www.pumpe24.de/pumpen/gartenpumpen.html"
response = scraper.make_request(category_url)

if response:
    soup = BeautifulSoup(response.text, 'html.parser')
    product_links = soup.select('a.product-item-link')
    test_urls = [link.get('href') for link in product_links[5:10]]  # Get products 6-10
    
    print("="*60)
    print(f"Testing 5 Products from Pumpe24")
    print("="*60)
    
    results = []
    for i, url in enumerate(test_urls, 1):
        product = scraper.scrape_product(url)
        if product:
            results.append(product)
            print(f"\n{i}. {product['name'][:50]}...")
            print(f"   Manufacturer: {product.get('manufacturer', 'N/A')}")
            print(f"   Article #: {product.get('article_number', 'N/A')}")
            print(f"   Price: {product.get('price_gross', 'N/A')}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    manufacturer_count = sum(1 for p in results if p.get('manufacturer'))
    article_count = sum(1 for p in results if p.get('article_number'))
    price_count = sum(1 for p in results if p.get('price_gross'))
    
    print(f"Manufacturer: {manufacturer_count}/{len(results)} ({manufacturer_count/len(results)*100:.0f}%)")
    print(f"Article #: {article_count}/{len(results)} ({article_count/len(results)*100:.0f}%)")
    print(f"Price: {price_count}/{len(results)} ({price_count/len(results)*100:.0f}%)")
else:
    print("Failed to fetch category page")
