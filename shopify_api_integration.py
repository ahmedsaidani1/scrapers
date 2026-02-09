"""
Shopify API Integration using OAuth 2.0 Client Credentials (2026+)
Uses the new Dev Dashboard app credentials.
"""
import requests
import json
import time
import csv
import glob
import os
from shopify_config import SHOPIFY_CONFIG


class ShopifyAPIIntegration:
    """
    Modern Shopify integration using OAuth 2.0 Client Credentials Grant.
    """
    
    def __init__(self):
        self.shop_url = SHOPIFY_CONFIG['shop_url']
        self.store_id = SHOPIFY_CONFIG.get('store_id', 'tbtgermany')
        self.client_id = SHOPIFY_CONFIG['client_id']
        self.client_secret = SHOPIFY_CONFIG['client_secret']
        self.api_version = SHOPIFY_CONFIG['api_version']
        
        self.access_token = None
        self.token_expires_at = 0
        
        print(f"Initialized Shopify API for {self.shop_url}")
    
    def get_access_token(self):
        """Get access token using Client Credentials Grant."""
        # Check if we have a valid cached token
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        print("Getting new access token...")
        
        # Token endpoint
        token_url = f"https://{self.shop_url}/admin/oauth/access_token"
        
        # Request payload
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(token_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 86400)  # 24 hours
                self.token_expires_at = time.time() + expires_in - 300  # Refresh 5 min early
                
                print(f"✓ Access token obtained (expires in {expires_in}s)")
                return self.access_token
            else:
                print(f"✗ Failed to get token: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ Error getting token: {e}")
            return None
    
    def test_connection(self):
        """Test API connection."""
        token = self.get_access_token()
        if not token:
            return False
        
        print("\nTesting API connection...")
        
        url = f"https://{self.shop_url}/admin/api/{self.api_version}/shop.json"
        headers = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                shop_data = response.json()
                shop_name = shop_data.get('shop', {}).get('name', 'Unknown')
                print(f"✓ Connected to: {shop_name}")
                return True
            else:
                print(f"✗ Connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def find_product_by_sku(self, sku):
        """Find existing product by SKU using GraphQL."""
        if not sku:
            return None
        
        token = self.get_access_token()
        if not token:
            return None
        
        # GraphQL query to search products by SKU
        query = """
        query searchProducts($query: String!) {
          products(first: 1, query: $query) {
            edges {
              node {
                id
                title
                variants(first: 1) {
                  edges {
                    node {
                      id
                      sku
                      price
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        variables = {
            'query': f'sku:{sku}'
        }
        
        url = f"https://{self.shop_url}/admin/api/{self.api_version}/graphql.json"
        headers = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                url,
                json={'query': query, 'variables': variables},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                edges = result.get('data', {}).get('products', {}).get('edges', [])
                
                if edges:
                    product = edges[0]['node']
                    variant = product['variants']['edges'][0]['node']
                    return {
                        'product_id': product['id'],
                        'variant_id': variant['id'],
                        'title': product['title'],
                        'current_price': variant['price']
                    }
            
            return None
            
        except Exception as e:
            print(f"  ⚠ Error searching for SKU {sku}: {e}")
            return None
    
    def update_product_price(self, variant_id, new_price):
        """Update product variant price using GraphQL."""
        token = self.get_access_token()
        if not token:
            return False
        
        mutation = """
        mutation productVariantUpdate($input: ProductVariantInput!) {
          productVariantUpdate(input: $input) {
            productVariant {
              id
              price
            }
            userErrors {
              field
              message
            }
          }
        }
        """
        
        variables = {
            'input': {
                'id': variant_id,
                'price': new_price
            }
        }
        
        url = f"https://{self.shop_url}/admin/api/{self.api_version}/graphql.json"
        headers = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                url,
                json={'query': mutation, 'variables': variables},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('data', {}).get('productVariantUpdate', {}).get('productVariant'):
                    return True
                else:
                    errors = result.get('data', {}).get('productVariantUpdate', {}).get('userErrors', [])
                    if errors:
                        print(f"  ✗ Update errors: {errors}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"  ✗ Update error: {e}")
            return False
    
    def create_or_update_product(self, product_data):
        """Create new product or update existing one if duplicate found."""
        # Get product name from various possible column names
        title = (product_data.get('Title') or 
                product_data.get('name') or 
                product_data.get('product_name') or 
                'Untitled Product')
        
        # Get price from various possible column names
        price_str = (product_data.get('Variant Price') or 
                    product_data.get('price_gross') or 
                    product_data.get('price') or 
                    '0')
        price = self._apply_markup(price_str)
        
        # Get SKU
        sku = (product_data.get('Variant SKU') or 
              product_data.get('article_number') or 
              product_data.get('sku') or 
              '')
        
        # Check for existing product by SKU
        if sku:
            existing = self.find_product_by_sku(sku)
            
            if existing:
                # Product exists - update price if different
                current_price = existing['current_price']
                
                if current_price != price:
                    if self.update_product_price(existing['variant_id'], price):
                        print(f"  ✓ Updated: {title} (€{current_price} → €{price})")
                        return {'action': 'updated', 'product': existing}
                    else:
                        print(f"  ✗ Failed to update: {title}")
                        return None
                else:
                    print(f"  ⊙ Unchanged: {title} (€{price})")
                    return {'action': 'unchanged', 'product': existing}
        
        # Product doesn't exist - create new one
        return self.create_product(product_data)
    
    def create_product(self, product_data):
        """Create a product using GraphQL Admin API with productSet mutation."""
        token = self.get_access_token()
        if not token:
            return None
        
        # Get product name from various possible column names
        title = (product_data.get('Title') or 
                product_data.get('name') or 
                product_data.get('product_name') or 
                'Untitled Product')
        
        # Get price from various possible column names
        price_str = (product_data.get('Variant Price') or 
                    product_data.get('price_gross') or 
                    product_data.get('price') or 
                    '0')
        price = self._apply_markup(price_str)
        
        # Get SKU
        sku = (product_data.get('Variant SKU') or 
              product_data.get('article_number') or 
              product_data.get('sku') or 
              '')
        
        # Get barcode/EAN
        barcode = (product_data.get('Variant Barcode') or 
                  product_data.get('ean') or 
                  '')
        
        # Get image URL
        image_url = (product_data.get('Image Src') or 
                    product_data.get('product_image') or 
                    '')
        
        # GraphQL mutation using productSet (supports variants and files in one call)
        mutation = """
        mutation productSet($input: ProductSetInput!) {
          productSet(input: $input) {
            product {
              id
              title
              handle
            }
            userErrors {
              field
              message
            }
          }
        }
        """
        
        # Build product input with all fields at root level
        vendor = product_data.get('Vendor') or product_data.get('manufacturer') or ''
        product_type = product_data.get('Type') or product_data.get('category') or ''
        
        # Truncate product_type if too long (max 255 chars)
        if len(product_type) > 255:
            product_type = product_type[:252] + '...'
        
        product_input = {
            'title': title,
            'descriptionHtml': self._build_description(product_data),
            'vendor': vendor,
            'productType': product_type,
            'tags': ['imported', 'scraped'],
            'status': 'DRAFT',
            # For simple products, add a default "Title" option
            'productOptions': [{
                'name': 'Title',
                'values': [{'name': 'Default Title'}]
            }]
        }
        
        # Add variant with price, SKU, barcode
        variants_input = [{
            'optionValues': [{'optionName': 'Title', 'name': 'Default Title'}],
            'price': price
        }]
        
        if sku:
            variants_input[0]['sku'] = sku
        if barcode:
            variants_input[0]['barcode'] = barcode
        
        product_input['variants'] = variants_input
        
        # Debug: Print price being sent
        print(f"  → Price being sent: {price}")
        
        # Add files (images) if image URL exists and is valid
        if image_url and image_url.startswith('http'):
            product_input['files'] = [{
                'originalSource': image_url,
                'contentType': 'IMAGE'
            }]
        
        variables = {
            'input': product_input
        }
        
        url = f"https://{self.shop_url}/admin/api/{self.api_version}/graphql.json"
        headers = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                url,
                json={'query': mutation, 'variables': variables},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('data', {}).get('productSet', {}).get('product'):
                    product = result['data']['productSet']['product']
                    print(f"  ✓ Created: {product['title']}")
                    return {'action': 'created', 'product': product}
                else:
                    errors = result.get('data', {}).get('productSet', {}).get('userErrors', [])
                    if errors:
                        print(f"  ✗ Errors: {errors}")
                    else:
                        print(f"  ✗ Unknown error: {result}")
                    return None
            else:
                print(f"  ✗ Failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None
    
    def sync_from_csv(self, csv_file, max_products=None):
        """Sync products from CSV file."""
        print(f"\n{'='*70}")
        print(f"Syncing: {os.path.basename(csv_file)}")
        print(f"{'='*70}")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                products = list(reader)
            
            if max_products:
                products = products[:max_products]
            
            total = len(products)
            stats = {'created': 0, 'updated': 0, 'unchanged': 0, 'failed': 0}
            
            for i, product_data in enumerate(products, 1):
                # Get product name from various possible column names
                name = (product_data.get('Title') or 
                       product_data.get('name') or 
                       product_data.get('product_name') or 
                       'Unknown')
                
                print(f"[{i}/{total}] {name[:50]}...")
                
                result = self.create_or_update_product(product_data)
                
                if result:
                    action = result.get('action', 'unknown')
                    if action == 'created':
                        stats['created'] += 1
                    elif action == 'updated':
                        stats['updated'] += 1
                    elif action == 'unchanged':
                        stats['unchanged'] += 1
                else:
                    stats['failed'] += 1
                
                # Rate limiting (2 requests/second for GraphQL)
                time.sleep(0.6)
            
            print(f"\n✓ Created: {stats['created']}, Updated: {stats['updated']}, Unchanged: {stats['unchanged']}, Failed: {stats['failed']}")
            return stats
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return {'created': 0, 'updated': 0, 'unchanged': 0, 'failed': 0}
    
    def sync_all_csvs(self, max_per_file=None):
        """Sync all CSV files from data folder."""
        csv_files = glob.glob('data/*.csv')
        csv_files = [f for f in csv_files if os.path.getsize(f) > 100]
        
        if not csv_files:
            print("No CSV files found in data/")
            return
        
        print(f"\n{'='*70}")
        print(f"SHOPIFY API SYNC - {len(csv_files)} files")
        print(f"{'='*70}")
        
        total_stats = {'created': 0, 'updated': 0, 'unchanged': 0, 'failed': 0}
        
        for csv_file in csv_files:
            stats = self.sync_from_csv(csv_file, max_per_file)
            total_stats['created'] += stats.get('created', 0)
            total_stats['updated'] += stats.get('updated', 0)
            total_stats['unchanged'] += stats.get('unchanged', 0)
            total_stats['failed'] += stats.get('failed', 0)
        
        print(f"\n{'='*70}")
        print(f"TOTAL: Created {total_stats['created']}, Updated {total_stats['updated']}, Unchanged {total_stats['unchanged']}, Failed {total_stats['failed']}")
        print(f"{'='*70}")
    
    def _apply_markup(self, price_str):
        """Apply price markup."""
        if not price_str:
            return "0.00"
        
        try:
            # Clean the price string: remove quotes, €, spaces
            cleaned = str(price_str).replace('"', '').replace("'", '').replace('€', '').replace(' ', '').strip()
            
            if not cleaned or cleaned == '':
                return "0.00"
            
            # Handle German number format: 1.234,56 or 1234,56
            # If there's both dot and comma, dot is thousands separator
            if '.' in cleaned and ',' in cleaned:
                # German format: 1.234,56 → remove dots, replace comma with dot
                cleaned = cleaned.replace('.', '').replace(',', '.')
            elif ',' in cleaned:
                # Just comma: 1234,56 → replace comma with dot
                cleaned = cleaned.replace(',', '.')
            # else: already in correct format (1234.56)
            
            price = float(cleaned)
            
            if SHOPIFY_CONFIG['price_markup']['enabled']:
                percentage = SHOPIFY_CONFIG['price_markup']['percentage']
                fixed = SHOPIFY_CONFIG['price_markup']['fixed_amount']
                
                if percentage > 0:
                    price = price * (1 + percentage / 100)
                if fixed > 0:
                    price += fixed
            
            return f"{price:.2f}"
        except Exception as e:
            print(f"  ⚠ Price parsing error for '{price_str}': {e}")
            return "0.00"
    
    def _build_description(self, product_data):
        """Build product description HTML."""
        parts = []
        
        if product_data.get('name'):
            parts.append(f"<h2>{product_data['name']}</h2>")
        
        parts.append("<ul>")
        
        if product_data.get('manufacturer'):
            parts.append(f"<li><strong>Manufacturer:</strong> {product_data['manufacturer']}</li>")
        
        if product_data.get('article_number'):
            parts.append(f"<li><strong>SKU:</strong> {product_data['article_number']}</li>")
        
        if product_data.get('ean'):
            parts.append(f"<li><strong>EAN:</strong> {product_data['ean']}</li>")
        
        if product_data.get('category'):
            parts.append(f"<li><strong>Category:</strong> {product_data['category']}</li>")
        
        parts.append("</ul>")
        
        if product_data.get('product_url'):
            parts.append(f"<p><a href='{product_data['product_url']}' target='_blank'>View original</a></p>")
        
        return "".join(parts)


def main():
    """Test the integration."""
    import sys
    
    integration = ShopifyAPIIntegration()
    
    # Test connection
    if not integration.test_connection():
        print("\n✗ Connection test failed!")
        sys.exit(1)
    
    # Sync products
    max_products = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    print(f"\nSyncing up to {max_products} products per file...")
    integration.sync_all_csvs(max_per_file=max_products)


if __name__ == "__main__":
    main()
