"""
Shopify Integration Module
Handles pushing scraped products to Shopify store via Admin API.
"""
import csv
import json
import time
import logging
from typing import List, Dict, Optional, Any
import requests
from shopify_config import SHOPIFY_CONFIG


class ShopifyIntegration:
    """
    Integration with Shopify Admin API for product management.
    """
    
    def __init__(self):
        self.shop_url = SHOPIFY_CONFIG['shop_url']
        self.api_key = SHOPIFY_CONFIG['api_key']
        self.api_secret = SHOPIFY_CONFIG.get('api_secret', '')
        self.api_password = SHOPIFY_CONFIG.get('api_password', '')
        self.api_version = SHOPIFY_CONFIG['api_version']
        self.auth_method = SHOPIFY_CONFIG.get('auth_method', 'token')
        
        # Build base API URL based on auth method
        if self.auth_method == 'basic' and self.api_secret:
            # Use API key and secret for basic auth
            self.base_url = f"https://{self.api_key}:{self.api_secret}@{self.shop_url}/admin/api/{self.api_version}"
        else:
            # Use API key and password (access token)
            self.base_url = f"https://{self.api_key}:{self.api_password}@{self.shop_url}/admin/api/{self.api_version}"
        
        # Setup logging
        self.logger = logging.getLogger('shopify_integration')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.logger.info(f"Initialized Shopify integration for {self.shop_url}")
    
    def validate_config(self) -> bool:
        """Validate Shopify configuration."""
        if not self.shop_url:
            self.logger.error("Shop URL not configured in shopify_config.py")
            return False
        
        if self.auth_method == 'basic':
            if not self.api_secret:
                self.logger.error("API secret not configured in shopify_config.py")
                return False
        else:
            if not self.api_password:
                self.logger.error("API password not configured in shopify_config.py")
                return False
        
        return True
    
    def test_connection(self) -> bool:
        """Test connection to Shopify API."""
        try:
            url = f"{self.base_url}/shop.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                shop_data = response.json()
                shop_name = shop_data.get('shop', {}).get('name', 'Unknown')
                self.logger.info(f"✓ Successfully connected to Shopify store: {shop_name}")
                return True
            else:
                self.logger.error(f"Failed to connect: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def find_product_by_sku(self, sku: str) -> Optional[Dict]:
        """Find existing product by SKU."""
        try:
            # Search for product variants with this SKU
            url = f"{self.base_url}/products.json"
            params = {'fields': 'id,title,variants'}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                products = response.json().get('products', [])
                
                for product in products:
                    for variant in product.get('variants', []):
                        if variant.get('sku') == sku:
                            return product
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding product by SKU {sku}: {e}")
            return None
    
    def find_product_by_ean(self, ean: str) -> Optional[Dict]:
        """Find existing product by EAN (barcode)."""
        try:
            url = f"{self.base_url}/products.json"
            params = {'fields': 'id,title,variants'}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                products = response.json().get('products', [])
                
                for product in products:
                    for variant in product.get('variants', []):
                        if variant.get('barcode') == ean:
                            return product
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding product by EAN {ean}: {e}")
            return None
    
    def create_product(self, product_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new product in Shopify."""
        try:
            # Apply price markup if configured
            price = self._apply_markup(product_data.get('price_gross', ''))
            
            # Build Shopify product payload
            shopify_product = {
                'product': {
                    'title': product_data.get('name', product_data.get('title', 'Untitled')),
                    'body_html': self._build_description(product_data),
                    'vendor': product_data.get('manufacturer', SHOPIFY_CONFIG['defaults']['vendor']),
                    'product_type': product_data.get('category', SHOPIFY_CONFIG['defaults']['product_type']),
                    'tags': SHOPIFY_CONFIG['defaults']['tags'],
                    'published': SHOPIFY_CONFIG['defaults']['published'],
                    'variants': [
                        {
                            'sku': product_data.get('article_number', ''),
                            'barcode': product_data.get('ean', ''),
                            'price': price,
                            'inventory_management': 'shopify',
                            'inventory_policy': 'deny',  # Don't allow overselling
                        }
                    ],
                }
            }
            
            # Add product image if available
            if product_data.get('product_image'):
                shopify_product['product']['images'] = [
                    {'src': product_data['product_image']}
                ]
            
            # Add metafields for additional data
            metafields = []
            
            if product_data.get('product_url'):
                metafields.append({
                    'namespace': 'source',
                    'key': 'url',
                    'value': product_data['product_url'],
                    'type': 'url'
                })
            
            if product_data.get('price_net'):
                metafields.append({
                    'namespace': 'pricing',
                    'key': 'net_price',
                    'value': product_data['price_net'],
                    'type': 'single_line_text_field'
                })
            
            if metafields:
                shopify_product['product']['metafields'] = metafields
            
            # Make API request
            url = f"{self.base_url}/products.json"
            response = requests.post(url, json=shopify_product, timeout=30)
            
            if response.status_code == 201:
                created_product = response.json().get('product', {})
                self.logger.info(f"✓ Created product: {created_product.get('title')} (ID: {created_product.get('id')})")
                return created_product
            else:
                self.logger.error(f"Failed to create product: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating product: {e}")
            return None
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> bool:
        """Update an existing product in Shopify."""
        try:
            # Apply price markup if configured
            price = self._apply_markup(product_data.get('price_gross', ''))
            
            # Build update payload (only update price and inventory)
            update_payload = {
                'product': {
                    'id': product_id,
                    'variants': [
                        {
                            'price': price,
                        }
                    ]
                }
            }
            
            # Make API request
            url = f"{self.base_url}/products/{product_id}.json"
            response = requests.put(url, json=update_payload, timeout=30)
            
            if response.status_code == 200:
                self.logger.info(f"✓ Updated product ID {product_id} with new price: {price}")
                return True
            else:
                self.logger.error(f"Failed to update product: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating product: {e}")
            return False
    
    def sync_product(self, product_data: Dict[str, Any]) -> bool:
        """
        Sync a product to Shopify (create or update).
        Returns True if successful.
        """
        try:
            # Determine how to match existing products
            match_by = SHOPIFY_CONFIG.get('match_by', 'sku')
            existing_product = None
            
            if match_by == 'sku' and product_data.get('article_number'):
                existing_product = self.find_product_by_sku(product_data['article_number'])
            elif match_by == 'ean' and product_data.get('ean'):
                existing_product = self.find_product_by_ean(product_data['ean'])
            
            # Update or create
            if existing_product and SHOPIFY_CONFIG.get('update_existing', True):
                return self.update_product(existing_product['id'], product_data)
            elif not existing_product:
                result = self.create_product(product_data)
                return result is not None
            else:
                self.logger.info(f"Skipping existing product: {product_data.get('name')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error syncing product: {e}")
            return False
    
    def sync_from_csv(self, csv_file: str, max_products: int = None) -> Dict[str, int]:
        """
        Sync products from a CSV file to Shopify.
        Returns statistics: {'created': X, 'updated': Y, 'failed': Z}
        """
        stats = {'created': 0, 'updated': 0, 'failed': 0, 'skipped': 0}
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                products = list(reader)
            
            total = len(products) if not max_products else min(len(products), max_products)
            self.logger.info(f"Starting sync of {total} products from {csv_file}")
            
            for i, product_data in enumerate(products[:max_products] if max_products else products, 1):
                self.logger.info(f"[{i}/{total}] Processing: {product_data.get('name', 'Unknown')}")
                
                # Check if product exists
                match_by = SHOPIFY_CONFIG.get('match_by', 'sku')
                existing_product = None
                
                if match_by == 'sku' and product_data.get('article_number'):
                    existing_product = self.find_product_by_sku(product_data['article_number'])
                elif match_by == 'ean' and product_data.get('ean'):
                    existing_product = self.find_product_by_ean(product_data['ean'])
                
                # Sync product
                if existing_product and SHOPIFY_CONFIG.get('update_existing', True):
                    if self.update_product(existing_product['id'], product_data):
                        stats['updated'] += 1
                    else:
                        stats['failed'] += 1
                elif not existing_product:
                    if self.create_product(product_data):
                        stats['created'] += 1
                    else:
                        stats['failed'] += 1
                else:
                    stats['skipped'] += 1
                
                # Rate limiting (Shopify has 2 requests/second limit)
                time.sleep(0.6)
            
            self.logger.info(f"Sync complete: {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error syncing from CSV: {e}")
            return stats
    
    def _apply_markup(self, price_str: str) -> str:
        """Apply price markup if configured."""
        if not price_str:
            return "0.00"
        
        try:
            # Convert German format to float
            price = float(price_str.replace(',', '.'))
            
            # Apply markup
            if SHOPIFY_CONFIG['price_markup']['enabled']:
                percentage = SHOPIFY_CONFIG['price_markup']['percentage']
                fixed = SHOPIFY_CONFIG['price_markup']['fixed_amount']
                
                if percentage > 0:
                    price = price * (1 + percentage / 100)
                
                if fixed > 0:
                    price += fixed
            
            return f"{price:.2f}"
            
        except:
            return "0.00"
    
    def _build_description(self, product_data: Dict[str, Any]) -> str:
        """Build product description HTML."""
        parts = []
        
        if product_data.get('name'):
            parts.append(f"<h2>{product_data['name']}</h2>")
        
        parts.append("<ul>")
        
        if product_data.get('manufacturer'):
            parts.append(f"<li><strong>Manufacturer:</strong> {product_data['manufacturer']}</li>")
        
        if product_data.get('article_number'):
            parts.append(f"<li><strong>Article Number:</strong> {product_data['article_number']}</li>")
        
        if product_data.get('ean'):
            parts.append(f"<li><strong>EAN:</strong> {product_data['ean']}</li>")
        
        if product_data.get('category'):
            parts.append(f"<li><strong>Category:</strong> {product_data['category']}</li>")
        
        parts.append("</ul>")
        
        if product_data.get('product_url'):
            parts.append(f"<p><a href='{product_data['product_url']}' target='_blank'>View original product</a></p>")
        
        return "\n".join(parts)


def main():
    """Test Shopify integration."""
    import sys
    
    integration = ShopifyIntegration()
    
    # Validate configuration
    if not integration.validate_config():
        print("\n❌ Configuration incomplete. Please update shopify_config.py with:")
        print("  1. Your Shopify store URL")
        print("  2. Your API password/access token")
        sys.exit(1)
    
    # Test connection
    print("\nTesting Shopify connection...")
    if integration.test_connection():
        print("✓ Connection successful!")
    else:
        print("✗ Connection failed. Check your credentials.")
        sys.exit(1)
    
    # If CSV file provided, sync products
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        max_products = int(sys.argv[2]) if len(sys.argv) > 2 else None
        
        print(f"\nSyncing products from {csv_file}...")
        stats = integration.sync_from_csv(csv_file, max_products)
        
        print(f"\n{'='*60}")
        print(f"Sync Results:")
        print(f"  Created: {stats['created']}")
        print(f"  Updated: {stats['updated']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
