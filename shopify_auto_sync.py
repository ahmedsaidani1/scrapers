"""
Automated Shopify sync using Shopify Admin API.
This bypasses OAuth by using the Admin API access token directly.
"""
import requests
import csv
import time
import logging
from typing import Dict, List, Optional, Any
from shopify_config import SHOPIFY_CONFIG


class ShopifyAutoSync:
    """
    Automated Shopify sync using Admin API access token.
    No OAuth needed - just the access token from your app.
    """
    
    def __init__(self, access_token: str = None):
        """
        Initialize with Admin API access token.
        
        Args:
            access_token: Admin API access token (starts with shpat_)
                         If not provided, will try to get from config
        """
        self.store_id = SHOPIFY_CONFIG.get('store_id', 'tbtgermany')
        self.api_version = SHOPIFY_CONFIG.get('api_version', '2024-10')
        
        # Get access token
        self.access_token = access_token or SHOPIFY_CONFIG.get('access_token', '')
        
        if not self.access_token:
            raise ValueError("Admin API access token required! Add 'access_token' to shopify_config.py")
        
        # Build API URL
        self.base_url = f"https://admin.shopify.com/store/{self.store_id}/admin/api/{self.api_version}"
        
        # Setup logging
        self.logger = logging.getLogger('shopify_auto_sync')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers."""
        return {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            url = f"{self.base_url}/shop.json"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                shop = response.json().get('shop', {})
                self.logger.info(f"✓ Connected to: {shop.get('name', 'Unknown')}")
                return True
            else:
                self.logger.error(f"Connection failed: {response.status_code}")
                self.logger.error(f"Response: {response.text[:200]}")
                return False
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False
    
    def find_product_by_sku(self, sku: str) -> Optional[Dict]:
        """Find product by SKU."""
        try:
            # Use GraphQL for efficient search
            query = """
            query findProductBySku($query: String!) {
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
            
            url = f"{self.base_url}/graphql.json"
            payload = {
                'query': query,
                'variables': {'query': f'sku:{sku}'}
            }
            
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                edges = data.get('data', {}).get('products', {}).get('edges', [])
                if edges:
                    return edges[0]['node']
            
            return None
        except Exception as e:
            self.logger.error(f"Error finding SKU {sku}: {e}")
            return None
    
    def create_product(self, product_data: Dict) -> Optional[Dict]:
        """Create new product."""
        try:
            price = self._apply_markup(product_data.get('price_gross', '0'))
            
            payload = {
                'product': {
                    'title': product_data.get('name', 'Untitled'),
                    'body_html': self._build_description(product_data),
                    'vendor': product_data.get('manufacturer', ''),
                    'product_type': product_data.get('category', ''),
                    'tags': 'imported, scraped',
                    'status': 'draft',
                    'variants': [{
                        'sku': product_data.get('article_number', ''),
                        'barcode': product_data.get('ean', ''),
                        'price': price,
                        'inventory_management': 'shopify',
                        'inventory_policy': 'deny'
                    }]
                }
            }
            
            if product_data.get('product_image'):
                payload['product']['images'] = [{'src': product_data['product_image']}]
            
            url = f"{self.base_url}/products.json"
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            
            if response.status_code == 201:
                product = response.json().get('product', {})
                self.logger.info(f"✓ Created: {product.get('title')}")
                return product
            else:
                self.logger.error(f"Create failed: {response.status_code} - {response.text[:200]}")
                return None
        except Exception as e:
            self.logger.error(f"Error creating product: {e}")
            return None
    
    def update_product_price(self, product_id: str, variant_id: str, new_price: str) -> bool:
        """Update product price."""
        try:
            # Extract numeric IDs if GraphQL format
            if 'gid://' in str(product_id):
                product_id = product_id.split('/')[-1]
            if 'gid://' in str(variant_id):
                variant_id = variant_id.split('/')[-1]
            
            url = f"{self.base_url}/variants/{variant_id}.json"
            payload = {'variant': {'id': variant_id, 'price': new_price}}
            
            response = requests.put(url, json=payload, headers=self._get_headers(), timeout=30)
            
            if response.status_code == 200:
                self.logger.info(f"✓ Updated price: {new_price}")
                return True
            else:
                self.logger.error(f"Update failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Error updating price: {e}")
            return False
    
    def sync_from_csv(self, csv_file: str, max_products: int = None) -> Dict[str, int]:
        """
        Sync products from CSV to Shopify.
        
        Returns:
            Stats dict with created/updated/failed counts
        """
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'failed': 0}
        
        try:
            # Read CSV
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                products = list(reader)
            
            total = len(products) if not max_products else min(len(products), max_products)
            self.logger.info(f"Syncing {total} products from {csv_file}")
            
            for i, product_data in enumerate(products[:max_products] if max_products else products, 1):
                self.logger.info(f"[{i}/{total}] {product_data.get('name', 'Unknown')}")
                
                sku = product_data.get('article_number', '')
                if not sku:
                    self.logger.warning("  No SKU, skipping")
                    stats['skipped'] += 1
                    continue
                
                # Check if exists
                existing = self.find_product_by_sku(sku)
                
                if existing:
                    # Update price
                    new_price = self._apply_markup(product_data.get('price_gross', '0'))
                    variant = existing.get('variants', {}).get('edges', [{}])[0].get('node', {})
                    variant_id = variant.get('id', '')
                    
                    if self.update_product_price(existing['id'], variant_id, new_price):
                        stats['updated'] += 1
                    else:
                        stats['failed'] += 1
                else:
                    # Create new
                    if self.create_product(product_data):
                        stats['created'] += 1
                    else:
                        stats['failed'] += 1
                
                # Rate limiting
                time.sleep(0.5)
            
            self.logger.info(f"\nSync complete: {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Sync error: {e}")
            return stats
    
    def _apply_markup(self, price_str: str) -> str:
        """Apply price markup."""
        if not price_str:
            return "0.00"
        
        try:
            price = float(price_str.replace(',', '.').replace('€', '').strip())
            
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
    
    def _build_description(self, product: Dict) -> str:
        """Build product description."""
        parts = []
        
        if product.get('name'):
            parts.append(f"<h2>{product['name']}</h2>")
        
        parts.append("<ul>")
        if product.get('manufacturer'):
            parts.append(f"<li><strong>Manufacturer:</strong> {product['manufacturer']}</li>")
        if product.get('article_number'):
            parts.append(f"<li><strong>SKU:</strong> {product['article_number']}</li>")
        if product.get('ean'):
            parts.append(f"<li><strong>EAN:</strong> {product['ean']}</li>")
        parts.append("</ul>")
        
        if product.get('product_url'):
            parts.append(f"<p><a href='{product['product_url']}'>View original</a></p>")
        
        return "\n".join(parts)


def main():
    """Test the auto sync."""
    import sys
    
    print("=" * 70)
    print("SHOPIFY AUTO SYNC - Admin API Method")
    print("=" * 70)
    
    # Check for access token
    access_token = SHOPIFY_CONFIG.get('access_token', '')
    
    if not access_token:
        print("\n❌ Admin API access token not configured!")
        print("\nTo get your access token:")
        print("1. Go to Shopify Dev Dashboard")
        print("2. Click on your app 'product integration'")
        print("3. Go to Settings tab")
        print("4. Find 'Admin API access token' section")
        print("5. Copy the token (starts with shpat_)")
        print("\nThen add to shopify_config.py:")
        print("  'access_token': 'shpat_xxxxx',")
        sys.exit(1)
    
    # Initialize
    sync = ShopifyAutoSync()
    
    # Test connection
    print("\nTesting connection...")
    if not sync.test_connection():
        print("❌ Connection failed!")
        sys.exit(1)
    
    # Sync if CSV provided
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        max_products = int(sys.argv[2]) if len(sys.argv) > 2 else None
        
        print(f"\nSyncing from {csv_file}...")
        stats = sync.sync_from_csv(csv_file, max_products)
        
        print(f"\n{'='*70}")
        print("Results:")
        print(f"  Created: {stats['created']}")
        print(f"  Updated: {stats['updated']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Failed: {stats['failed']}")
        print(f"{'='*70}")
    else:
        print("\n✓ Connection successful!")
        print("\nTo sync products:")
        print("  python shopify_auto_sync.py data/heima24.csv 10")


if __name__ == "__main__":
    main()
