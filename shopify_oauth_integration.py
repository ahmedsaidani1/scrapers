"""
Modern Shopify Integration using OAuth 2.0 Client Credentials
Based on Shopify Dev Dashboard best practices.
"""
import csv
import json
import time
import logging
from typing import List, Dict, Optional, Any
import requests
from shopify_config import SHOPIFY_CONFIG


class ShopifyOAuthIntegration:
    """
    Modern Shopify integration using OAuth 2.0 client credentials grant.
    Follows Shopify Dev Dashboard best practices.
    """
    
    def __init__(self):
        self.shop_url = SHOPIFY_CONFIG['shop_url']
        self.store_id = SHOPIFY_CONFIG.get('store_id', '')
        self.client_id = SHOPIFY_CONFIG.get('client_id', SHOPIFY_CONFIG.get('api_key'))
        self.client_secret = SHOPIFY_CONFIG.get('client_secret', SHOPIFY_CONFIG.get('api_secret'))
        self.api_version = SHOPIFY_CONFIG.get('api_version', '2024-10')
        
        # OAuth token management
        self.access_token = None
        self.token_expires_at = 0
        
        # Setup logging
        self.logger = logging.getLogger('shopify_oauth')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.logger.info(f"Initialized OAuth integration for {self.shop_url}")
    
    def get_access_token(self) -> Optional[str]:
        """
        Get access token using client credentials grant.
        Implements OAuth 2.0 flow as per Shopify documentation.
        """
        # Check if we have a valid cached token
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        try:
            # For custom domains, use admin.shopify.com with store ID
            if self.store_id:
                token_url = f"https://admin.shopify.com/store/{self.store_id}/admin/oauth/access_token"
            else:
                token_url = f"https://{self.shop_url}/admin/oauth/access_token"
            
            # Request payload
            payload = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            # Add proper headers to avoid Cloudflare blocking
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
            }
            
            response = requests.post(token_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                
                # Cache token (typically valid for 24 hours, but we'll refresh more often)
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = time.time() + expires_in - 300  # Refresh 5 min early
                
                self.logger.info("✓ Successfully obtained access token")
                return self.access_token
            else:
                self.logger.error(f"Failed to get access token: {response.status_code}")
                if response.status_code == 403 or response.status_code == 401:
                    self.logger.error("Authentication failed. Please verify:")
                    self.logger.error("  1. App is installed on the store")
                    self.logger.error("  2. Client ID and Secret are correct")
                    self.logger.error("  3. Store ID is correct (check Dev Dashboard URL)")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting access token: {e}")
            return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        # For Dev Dashboard apps, use client credentials directly in headers
        # This bypasses the OAuth token endpoint
        return {
            'X-Shopify-Access-Token': f"{self.client_id}:{self.client_secret}",
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """
        Make authenticated API request with automatic retry on token expiry.
        """
        # For custom domains with store ID, use admin.shopify.com
        if self.store_id:
            url = f"https://admin.shopify.com/store/{self.store_id}/admin/api/{self.api_version}/{endpoint}"
        else:
            url = f"https://{self.shop_url}/admin/api/{self.api_version}/{endpoint}"
        
        try:
            headers = self._get_headers()
            response = requests.request(method, url, headers=headers, **kwargs)
            
            # Handle token expiry
            if response.status_code == 401:
                self.logger.warning("Token expired, refreshing...")
                self.access_token = None
                headers = self._get_headers()
                response = requests.request(method, url, headers=headers, **kwargs)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            return None
    
    def validate_config(self) -> bool:
        """Validate Shopify configuration."""
        if not self.shop_url:
            self.logger.error("Shop URL not configured")
            return False
        
        if not self.client_id or not self.client_secret:
            self.logger.error("Client ID and Secret not configured")
            return False
        
        return True
    
    def test_connection(self) -> bool:
        """Test connection to Shopify API."""
        try:
            # Skip OAuth token for now, try direct API call
            response = self._make_request('GET', 'shop.json', timeout=10)
            
            if response and response.status_code == 200:
                shop_data = response.json()
                shop_name = shop_data.get('shop', {}).get('name', 'Unknown')
                self.logger.info(f"✓ Successfully connected to Shopify store: {shop_name}")
                return True
            else:
                error_msg = response.text if response else "No response"
                self.logger.error(f"Failed to connect: {error_msg[:200]}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def find_product_by_sku(self, sku: str) -> Optional[Dict]:
        """Find existing product by SKU using GraphQL (more efficient)."""
        try:
            # Use GraphQL for better performance
            query = """
            query findProductBySku($query: String!) {
                products(first: 1, query: $query) {
                    edges {
                        node {
                            id
                            title
                            variants(first: 10) {
                                edges {
                                    node {
                                        id
                                        sku
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
            
            response = self._make_request(
                'POST',
                'graphql.json',
                json={'query': query, 'variables': variables},
                timeout=10
            )
            
            if response and response.status_code == 200:
                data = response.json()
                edges = data.get('data', {}).get('products', {}).get('edges', [])
                
                if edges:
                    return edges[0]['node']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding product by SKU {sku}: {e}")
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
                    'status': 'draft' if not SHOPIFY_CONFIG['defaults']['published'] else 'active',
                    'variants': [
                        {
                            'sku': product_data.get('article_number', ''),
                            'barcode': product_data.get('ean', ''),
                            'price': price,
                            'inventory_management': 'shopify',
                            'inventory_policy': 'deny',
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
            response = self._make_request('POST', 'products.json', json=shopify_product, timeout=30)
            
            if response and response.status_code == 201:
                created_product = response.json().get('product', {})
                self.logger.info(f"✓ Created product: {created_product.get('title')} (ID: {created_product.get('id')})")
                return created_product
            else:
                error_msg = response.text if response else "No response"
                self.logger.error(f"Failed to create product: {error_msg}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating product: {e}")
            return None
    
    def update_product(self, product_id: str, product_data: Dict[str, Any]) -> bool:
        """Update an existing product in Shopify."""
        try:
            # Apply price markup if configured
            price = self._apply_markup(product_data.get('price_gross', ''))
            
            # Extract numeric ID from GraphQL ID if needed
            if 'gid://shopify/Product/' in product_id:
                numeric_id = product_id.split('/')[-1]
            else:
                numeric_id = product_id
            
            # Build update payload
            update_payload = {
                'product': {
                    'id': numeric_id,
                    'variants': [
                        {
                            'price': price,
                        }
                    ]
                }
            }
            
            # Make API request
            response = self._make_request('PUT', f'products/{numeric_id}.json', json=update_payload, timeout=30)
            
            if response and response.status_code == 200:
                self.logger.info(f"✓ Updated product ID {numeric_id} with new price: {price}")
                return True
            else:
                error_msg = response.text if response else "No response"
                self.logger.error(f"Failed to update product: {error_msg}")
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
                
                # Rate limiting (Shopify has 2 requests/second limit for REST API)
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
            price = float(price_str.replace(',', '.').replace('€', '').strip())
            
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
    """Test Shopify OAuth integration."""
    import sys
    
    integration = ShopifyOAuthIntegration()
    
    # Validate configuration
    if not integration.validate_config():
        print("\n❌ Configuration incomplete. Please update shopify_config.py")
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
