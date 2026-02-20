"""
Test wasserpumpe scraper with 20 brand-name products to verify price extraction
"""
from wasserpumpe_scraper import WasserpumpeScraper


def main():
    print("="*60)
    print("Testing Wasserpumpe Scraper - 20 Brand Products")
    print("="*60)
    
    scraper = WasserpumpeScraper()
    
    # Get URLs from sitemap and filter for brand products
    print("\nFetching product URLs from sitemap...")
    all_urls = scraper._extract_urls_from_sitemap(max_urls=None)
    
    print(f"Total URLs found: {len(all_urls)}")
    
    # Filter for brand-name products (these are real products, not guides)
    brands = ['dab-', 'grundfos-', 'pedrollo-', 'ebara-', 'wilo-', 'lowara-', 
              'calpeda-', 'nocchi-', 'leo-', 'espa-', 'pentax-', 'speroni-']
    
    brand_products = []
    for url in all_urls:
        url_lower = url.lower()
        if any(brand in url_lower for brand in brands):
            brand_products.append(url)
            if len(brand_products) >= 20:
                break
    
    print(f"Brand product URLs found: {len(brand_products)}")
    
    if not brand_products:
        print("No brand products found!")
        return
    
    # Scrape each product
    print("\nScraping products...")
    products = []
    
    for i, url in enumerate(brand_products, 1):
        print(f"[{i}/20] {url}")
        product = scraper.scrape_product(url)
        if product:
            products.append(product)
    
    print(f"\nSuccessfully scraped: {len(products)}/20")
    
    if not products:
        print("No products scraped!")
        return
    
    # Analyze the results
    print("\n" + "="*60)
    print("FIELD COVERAGE")
    print("="*60)
    
    fields = {
        'manufacturer': 'Manufacturer',
        'category': 'Category',
        'name': 'Name',
        'article_number': 'Article #',
        'price_gross': 'Price Gross',
        'price_net': 'Price Net',
        'ean': 'EAN',
        'product_image': 'Image'
    }
    
    for field_key, field_name in fields.items():
        filled = sum(1 for p in products if p.get(field_key) and str(p.get(field_key)).strip())
        percentage = (filled / len(products)) * 100
        print(f"  {field_name:20s}: {filled}/{len(products)} ({percentage:.0f}%)")
    
    # Check price validity
    print("\n" + "="*60)
    print("PRICE ANALYSIS")
    print("="*60)
    
    valid_prices = 0
    invalid_prices = 0
    price_samples = []
    
    for p in products:
        price_gross = str(p.get('price_gross', '')).strip()
        price_net = str(p.get('price_net', '')).strip()
        
        if price_gross and price_gross not in ['0,00', '0,40', '']:
            valid_prices += 1
            if len(price_samples) < 10:
                price_samples.append({
                    'name': p.get('name', '')[:50],
                    'manufacturer': p.get('manufacturer', ''),
                    'article': p.get('article_number', ''),
                    'price_gross': price_gross,
                    'price_net': price_net
                })
        else:
            invalid_prices += 1
    
    print(f"Valid prices (> 0,40): {valid_prices}/{len(products)}")
    print(f"Invalid/missing prices: {invalid_prices}/{len(products)}")
    
    if price_samples:
        print("\n" + "="*60)
        print("SAMPLE PRODUCTS WITH VALID PRICES")
        print("="*60)
        
        for i, sample in enumerate(price_samples, 1):
            print(f"\n{i}. {sample['name']}...")
            print(f"   Manufacturer: {sample['manufacturer']}")
            print(f"   Article #: {sample['article']}")
            print(f"   Price Gross: {sample['price_gross']}")
            print(f"   Price Net: {sample['price_net']}")
    
    # Show all products summary
    print("\n" + "="*60)
    print("ALL PRODUCTS SUMMARY")
    print("="*60)
    
    for i, p in enumerate(products, 1):
        manufacturer = p.get('manufacturer', 'N/A')
        name = p.get('name', 'N/A')[:40]
        article = p.get('article_number', 'N/A')
        price = p.get('price_gross', 'N/A')
        
        status = "✓" if price and price not in ['0,00', '0,40', 'N/A', ''] else "✗"
        print(f"{i:2d}. {status} {manufacturer:12s} | {name:40s} | {article:15s} | {price:10s}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
