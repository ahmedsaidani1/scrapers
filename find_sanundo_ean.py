"""Find EAN in sanundo HTML"""
from bs4 import BeautifulSoup

with open('sanundo_debug.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Check for data-ean attribute
elems_data_ean = soup.find_all(attrs={'data-ean': True})
print(f"Elements with data-ean: {len(elems_data_ean)}")
for e in elems_data_ean[:5]:
    print(f"  {e.name}: {e.get('data-ean')}")

# Check for any element containing "ean" in attributes
print("\nElements with 'ean' in attribute names:")
for elem in soup.find_all():
    for attr in elem.attrs:
        if 'ean' in attr.lower():
            print(f"  {elem.name}.{attr}: {elem[attr]}")
            break

# Check for gtin attributes
elems_gtin = soup.find_all(attrs={'itemprop': 'gtin13'})
print(f"\nElements with itemprop='gtin13': {len(elems_gtin)}")
for e in elems_gtin[:5]:
    print(f"  {e.name}: {e.get_text(strip=True)[:50]}")

# Search in product details table
print("\nSearching for product details table...")
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

for i, table in enumerate(tables[:3], 1):
    text = table.get_text()
    if 'EAN' in text or 'GTIN' in text or 'Artikel' in text:
        print(f"\nTable {i} contains relevant text:")
        rows = table.find_all('tr')
        for row in rows[:10]:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                if key:
                    print(f"  {key}: {value}")
