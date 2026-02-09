"""Test price parsing and debug what's being sent to Shopify"""
import csv
from shopify_api_integration import ShopifyAPIIntegration

# Read one product from heima24.csv
with open('data/heima24.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    product = next(reader)

print("CSV Product Data:")
print(f"  name: {product.get('name')}")
print(f"  price_net: {repr(product.get('price_net'))}")
print(f"  price_gross: {repr(product.get('price_gross'))}")
print(f"  price: {repr(product.get('price'))}")

# Test price extraction
integration = ShopifyAPIIntegration()

price_str = (product.get('Variant Price') or 
            product.get('price_gross') or 
            product.get('price') or 
            '0')

print(f"\nExtracted price_str: {repr(price_str)}")

parsed_price = integration._apply_markup(price_str)
print(f"Parsed price: {parsed_price}")

# Show what would be sent to Shopify
print(f"\nThis would be sent to Shopify as: {parsed_price}")
