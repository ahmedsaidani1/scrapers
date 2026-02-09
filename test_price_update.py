"""Test price update functionality"""
import csv

# Read heima24.csv
with open('data/heima24.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Change first product price
print(f"Original price: {rows[0]['price_gross']}")
rows[0]['price_gross'] = "500,00"  # Changed from 403,67
print(f"New price: {rows[0]['price_gross']}")

# Write back
with open('data/heima24.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\n✓ Price updated in CSV. Now run: python shopify_api_integration.py 1")
print("  It should detect the price change and update Shopify!")
