"""Analyze ST-Shop24 Magento structure"""
import requests
from bs4 import BeautifulSoup
import json

print("="*70)
print("ANALYZING ST-SHOP24 STRUCTURE")
print("="*70)

# Test homepage
print("\n1. Checking homepage...")
r = requests.get("https://st-shop24.de")
soup = BeautifulSoup(r.text, 'html.parser')

# Look for product listings
products = soup.select('.product-item, .item, .product')
print(f"   Products on homepage: {len(products)}")

# Get a category URL from sitemap
print("\n2. Getting category URLs from sitemap...")
r_sitemap = requests.get("https://st-shop24.de/sitemap.xml")
soup_sitemap = BeautifulSoup(r_sitemap.text, 'xml')
category_urls = [loc.text for loc in soup_sitemap.find_all('loc') if loc.text.count('/') == 4 and '.html' in loc.text]
print(f"   Found {len(category_urls)} category URLs")

# Test a category page
if category_urls:
    test_category = category_urls[0]
    print(f"\n3. Testing category: {test_category}")
    r_cat = requests.get(test_category)
    soup_cat = BeautifulSoup(r_cat.text, 'html.parser')
    
    # Look for product items with various Magento selectors
    selectors = [
        '.product-item',
        '.item.product',
        '.products-grid .item',
        '.category-products .item',
        'li.item.product',
        '.product-item-info'
    ]
    
    for selector in selectors:
        items = soup_cat.select(selector)
        if items:
            print(f"   ✓ Found {len(items)} products with selector: {selector}")
            
            # Get first product details
            first_item = items[0]
            link = first_item.select_one('a')
            name = first_item.select_one('.product-name, .product-item-name, h2, h3')
            price = first_item.select_one('.price, .price-box')
            
            if link:
                product_url = link.get('href')
                print(f"   Sample product URL: {product_url}")
                print(f"   Sample product name: {name.text.strip() if name else 'N/A'}")
                print(f"   Sample product price: {price.text.strip() if price else 'N/A'}")
                
                # Test the product page
                print(f"\n4. Testing product page: {product_url}")
                r_prod = requests.get(product_url)
                soup_prod = BeautifulSoup(r_prod.text, 'html.parser')
                
                prod_title = soup_prod.select_one('h1, .product-name')
                prod_price = soup_prod.select_one('.price, .price-box .price')
                prod_sku = soup_prod.select_one('.sku, [itemprop="sku"]')
                prod_image = soup_prod.select_one('.product-image img, .gallery-placeholder img')
                
                print(f"   Title: {prod_title.text.strip() if prod_title else 'N/A'}")
                print(f"   Price: {prod_price.text.strip() if prod_price else 'N/A'}")
                print(f"   SKU: {prod_sku.text.strip() if prod_sku else 'N/A'}")
                print(f"   Image: {prod_image.get('src') if prod_image else 'N/A'}")
                
            break

print("\n" + "="*70)
