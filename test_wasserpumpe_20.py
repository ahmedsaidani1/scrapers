"""
Test wasserpumpe scraper with 20 products to verify price extraction
"""
from wasserpumpe_scraper import WasserpumpeScraper


def main():
    print("="*60)
    print("Testing Wasserpumpe Scraper - 20 Products")
    print("="*60)
    
    scraper = WasserpumpeScraper()
    
    # Run the scraper with max 20 products
    print("\nRunning scraper with max_products=20...")
    scraper.run(max_products=20)
    
    # Read the output CSV
    import csv
    csv_file = scraper.get_output_file()
    
    print(f"\nReading results from: {csv_file}")
    
    products = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        products = list(reader)
    
    print(f"\nTotal products scraped: {len(products)}")
    
    if not products:
        print("No products found!")
        return
    
    # Analyze the results
    print("\n" + "="*60)
    print("FIELD COVERAGE")
    print("="*60)
    
    fields = ['Hersteller', 'Kategorie', 'Name', 'Artikelnummer', 
              'Preis_Brutto', 'Preis_Netto', 'EAN', 'Produktbild']
    
    for field in fields:
        filled = sum(1 for p in products if p.get(field) and p.get(field).strip())
        percentage = (filled / len(products)) * 100
        print(f"  {field:20s}: {filled}/{len(products)} ({percentage:.0f}%)")
    
    # Check price validity
    print("\n" + "="*60)
    print("PRICE ANALYSIS")
    print("="*60)
    
    valid_prices = 0
    invalid_prices = 0
    price_samples = []
    
    for p in products:
        price_gross = p.get('Preis_Brutto', '').strip()
        price_net = p.get('Preis_Netto', '').strip()
        
        if price_gross and price_gross not in ['0,00', '0,40']:
            valid_prices += 1
            if len(price_samples) < 10:
                price_samples.append({
                    'name': p.get('Name', '')[:40],
                    'manufacturer': p.get('Hersteller', ''),
                    'article': p.get('Artikelnummer', ''),
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
        manufacturer = p.get('Hersteller', 'N/A')
        name = p.get('Name', 'N/A')[:50]
        article = p.get('Artikelnummer', 'N/A')
        price = p.get('Preis_Brutto', 'N/A')
        
        status = "✓" if price and price not in ['0,00', '0,40', 'N/A'] else "✗"
        print(f"{i:2d}. {status} {manufacturer:15s} | {name:50s} | {article:15s} | {price:10s}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
