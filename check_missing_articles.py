"""Check products without article numbers"""
import csv

with open('data/selfio.csv', encoding='utf-8') as f:
    products = list(csv.DictReader(f))

no_article = [p for p in products if not p.get('Artikelnummer') or not p['Artikelnummer'].strip()]

print(f"Products without article number: {len(no_article)}/{len(products)}\n")

for p in no_article[:5]:
    print(f"{p['Name'][:60]}...")
    print(f"  URL: {p['Produkt_URL']}")
    print()
