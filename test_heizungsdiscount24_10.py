"""
Test heizungsdiscount24 scraper with 10 products
"""
from heizungsdiscount24_scraper import Heizungsdiscount24Scraper


def main():
    print("="*60)
    print("Testing Heizungsdiscount24 Scraper - 10 Products")
    print("="*60)
    
    scraper = Heizungsdiscount24Scraper()
    
    # Run the scraper with max 10 products
    print("\nRunning scraper with max_products=10...")
    scraper.run(max_products=10)
    
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
    
    # Show sample products
    print("\n" + "="*60)
    print("SAMPLE PRODUCTS")
    print("="*60)
    
    for i, p in enumerate(products[:10], 1):
        manufacturer = p.get('Hersteller', 'N/A')
        name = p.get('Name', 'N/A')[:50]
        article = p.get('Artikelnummer', 'N/A')
        price = p.get('Preis_Brutto', 'N/A')
        
        print(f"\n{i}. {name}...")
        print(f"   Manufacturer: {manufacturer}")
        print(f"   Article #: {article}")
        print(f"   Price: {price}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
