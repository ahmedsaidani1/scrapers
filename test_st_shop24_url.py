"""Test ST-Shop24 URL structure"""
import requests
from bs4 import BeautifulSoup

# Test a deeper URL from sitemap
test_url = "https://st-shop24.de/motoren/baugroesse-b3/2-polig-3000-u-min.html"
print(f"Testing: {test_url}\n")

r = requests.get(test_url)
soup = BeautifulSoup(r.text, 'html.parser')

# Check if it's a product or category page
title = soup.find('h1')
price = soup.select_one('.price')
sku = soup.select_one('.sku')
product_title = soup.select_one('.product_title')
woo_price = soup.select_one('.woocommerce-Price-amount')

print(f"Title: {title.text.strip() if title else 'None'}")
print(f"Product title: {product_title.text.strip() if product_title else 'None'}")
print(f"Price element: {bool(price)}")
print(f"WooCommerce price: {woo_price.text.strip() if woo_price else 'None'}")
print(f"SKU element: {bool(sku)}")

# Check for product grid (category) vs single product
product_grid = soup.select('.products .product')
single_product = soup.select_one('.single-product')

print(f"\nProduct grid items: {len(product_grid)}")
print(f"Single product page: {bool(single_product)}")

if product_grid:
    print("\nThis is a CATEGORY page with products:")
    for item in product_grid[:3]:
        link = item.select_one('a')
        if link:
            print(f"  Product link: {link.get('href')}")
