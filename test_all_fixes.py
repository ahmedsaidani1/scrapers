"""
Comprehensive test for all scraper fixes
Tests manufacturer, article number, price, and EAN extraction
"""
import csv
from wolfonlineshop_scraper import WolfonlineshopScraper
from wasserpumpe_scraper import WasserpumpeScraper
from heizungsdiscount24_scraper import Heizungsdiscount24Scraper
from selfio_scraper import SelfioScraper
from pumpe24_scraper import Pumpe24Scraper
from sanundo_scraper import SanundoScraper


def test_scraper(scraper_name, scraper_class, test_count=5):
    """Test a scraper with a small number of products"""
    print(f"\n{'='*70}")
    print(f"Testing {scraper_name.upper()}")
    print(f"{'='*70}")
    
    scraper = scraper_class()
    
    # Run scraper
    print(f"Running scraper with max_products={test_count}...")
    scraper.run(max_products=test_count)
    
    # Read results
    csv_file = scraper.get_output_file()
    products = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            products = list(reader)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None
    
    if not products:
        print("No products scraped!")
        return None
    
    # Calculate coverage
    fields = {
        'Hersteller': 'Manufacturer',
        'Artikelnummer': 'Article #',
        'Preis_Brutto': 'Price',
        'EAN': 'EAN'
    }
    
    results = {}
    for field, label in fields.items():
        filled = sum(1 for p in products if p.get(field) and p.get(field).strip())
        percentage = (filled / len(products)) * 100
        results[label] = (filled, len(products), percentage)
        print(f"  {label:15s}: {filled}/{len(products)} ({percentage:.0f}%)")
    
    # Show sample
    print(f"\n  Sample product:")
    p = products[0]
    print(f"    Name: {p['Name'][:50]}...")
    print(f"    Manufacturer: {p.get('Hersteller', 'N/A')}")
    print(f"    Article #: {p.get('Artikelnummer', 'N/A')}")
    print(f"    Price: {p.get('Preis_Brutto', 'N/A')}")
    print(f"    EAN: {p.get('EAN', 'N/A')}")
    
    return results


def main():
    print("="*70)
    print("COMPREHENSIVE SCRAPER FIX TEST")
    print("="*70)
    print("\nTesting all 6 fixed scrapers with 5 products each...")
    
    scrapers = [
        ("wolfonlineshop", WolfonlineshopScraper),
        ("wasserpumpe", WasserpumpeScraper),
        ("heizungsdiscount24", Heizungsdiscount24Scraper),
        ("selfio", SelfioScraper),
        ("pumpe24", Pumpe24Scraper),
        ("sanundo", SanundoScraper),
    ]
    
    all_results = {}
    
    for name, scraper_class in scrapers:
        try:
            results = test_scraper(name, scraper_class, test_count=5)
            if results:
                all_results[name] = results
        except Exception as e:
            print(f"\n  ERROR: {e}")
            all_results[name] = None
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY - ALL SCRAPERS")
    print("="*70)
    
    print(f"\n{'Scraper':<20} {'Manufacturer':<15} {'Article #':<15} {'Price':<15} {'EAN':<15}")
    print("-"*70)
    
    for name, results in all_results.items():
        if results:
            mfr = f"{results['Manufacturer'][0]}/{results['Manufacturer'][1]} ({results['Manufacturer'][2]:.0f}%)"
            art = f"{results['Article #'][0]}/{results['Article #'][1]} ({results['Article #'][2]:.0f}%)"
            prc = f"{results['Price'][0]}/{results['Price'][1]} ({results['Price'][2]:.0f}%)"
            ean = f"{results['EAN'][0]}/{results['EAN'][1]} ({results['EAN'][2]:.0f}%)"
            print(f"{name:<20} {mfr:<15} {art:<15} {prc:<15} {ean:<15}")
        else:
            print(f"{name:<20} {'FAILED':<15}")
    
    print("\n" + "="*70)
    print("Test complete!")
    print("="*70)


if __name__ == "__main__":
    main()
