"""Check existing pumpe24 data"""
import csv

with open('data/pumpe24.csv', encoding='utf-8') as f:
    products = list(csv.DictReader(f))

print(f"Total products: {len(products)}\n")

# Check field coverage
fields = ['Hersteller', 'Artikelnummer', 'Preis_Brutto']
for field in fields:
    filled = sum(1 for p in products if p.get(field) and p[field].strip())
    percentage = (filled / len(products)) * 100 if products else 0
    print(f"{field:20s}: {filled}/{len(products)} ({percentage:.0f}%)")

print("\nFirst 5 products:")
for i, p in enumerate(products[:5], 1):
    print(f"\n{i}. {p['Name'][:50]}...")
    print(f"   Manufacturer: {p.get('Hersteller', 'N/A')}")
    print(f"   Article: {p.get('Artikelnummer', 'N/A')}")
    print(f"   Price: {p.get('Preis_Brutto', 'N/A')}")
    print(f"   URL: {p['Produkt_URL']}")
