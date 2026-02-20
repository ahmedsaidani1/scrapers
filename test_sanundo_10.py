"""Test sanundo with 10 products"""
from sanundo_scraper import SanundoScraper

scraper = SanundoScraper()

print("="*60)
print("Testing Sanundo Scraper - 10 Products")
print("="*60)

# Run with max 10 products
scraper.run(max_products=10)

# Read results
import csv
csv_file = scraper.get_output_file()

products = []
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    products = list(reader)

print(f"\nTotal products scraped: {len(products)}")

# Field coverage
print("\n" + "="*60)
print("FIELD COVERAGE")
print("="*60)

fields = ['Hersteller', 'Kategorie', 'Name', 'Artikelnummer', 
          'Preis_Brutto', 'Preis_Netto', 'EAN', 'Produktbild']

for field in fields:
    filled = sum(1 for p in products if p.get(field) and p.get(field).strip())
    percentage = (filled / len(products)) * 100 if products else 0
    print(f"  {field:20s}: {filled}/{len(products)} ({percentage:.0f}%)")

# Sample products
print("\n" + "="*60)
print("SAMPLE PRODUCTS")
print("="*60)

for i, p in enumerate(products[:5], 1):
    print(f"\n{i}. {p['Name'][:50]}...")
    print(f"   Manufacturer: {p.get('Hersteller', 'N/A')}")
    print(f"   Article #: {p.get('Artikelnummer', 'N/A')}")
    print(f"   EAN: {p.get('EAN', 'N/A')}")
    print(f"   Price: {p.get('Preis_Brutto', 'N/A')}")

print("\n" + "="*60)
