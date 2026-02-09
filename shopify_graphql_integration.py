"""
Shopify GraphQL Integration for Automated Product Sync
Uses Shopify Admin API (GraphQL) which still works after Jan 2025
"""
import json
import time
import csv
import requests
from typing import List, Dict, Optional
import logging


class ShopifyGraphQLIntegration:
    """
    Automated Shopify integration using GraphQL Admin API.
    This works with access tokens from Shopify admin.
    """
    
    def __init__(self, shop_url: str, access_token: str):
        """
        Initialize with shop URL and access token.
        
        Args:
            shop_url: Your shop domain (e.g., 'tbbt.myshopify.com' or 'tbbt.de')
            access_token: Admin API access token (from Shopify admin)
        """
        # Handle custom domains
        if not shop_url.endswith('.myshopify.com'):
            # For custom domains, we need the myshopify.com URL
            # User will need to provide this
            self.shop_url = shop_url
        else:
            self.shop_url = shop_url
        
        self.access_token = access_token
        self.api_url = f"https://{self.shop_url}/admin/api/2024-01/graphql.json"
        
        # Setup logging
        self.logger = logging.getLogger('shopify_graphql')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _make_request(self, query: str, variables: Dict = None) -> Dict:
        """Make GraphQL API request."""
        headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': self.access_token
        }
        
        payload = {'query': query}
        if variables:
            payload['variables'] = variables
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test API connection."""
        query = """
        {
            shop {
                name
                email
            }
        }
        """
        
        result = self._make_request(query)
        
        if result and 'data' in result and 'shop' in result['data']:
            shop_name = result['data']['shop']['name']
            self.logger.info(f"✓ Connected to: {shop_name}")
            return True
        else:
            self.logger.error("✗ Connection failed")
            if result and 'errors' in result:
                self.logger.error(f"Errors: {result['errors']}")
            return False
    
    def create_product(self, product_data: Dict) -> Optional[str]:
        """
        Create a product using GraphQL.
        Returns product ID if successful.
        """
        mutation = """
        mutation productCreate($input: ProductInput!) {
            productCreate(input: $input) {
                product {
                    id
                    title
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
        
        # Build product input
        product_input = {
            'title': product_data.get('name', product_data.get('title', 'Untitled')),
            'descriptionHtml': self._build_description(product_data),
            'vendor': product_data.get('manufacturer', ''),
            'productType': product_data.get('category', ''),
            'tags': ['imported', 'scraped'],
            'status': 'DRAFT',  # Don't auto-publish
            'variants': [
                {
                    'sku': product_data.get('article_number', ''),
                    'barcode': product_data.get('ean', ''),
                    'price': self._format_price(product_data.get('price_gross', '0')),
                    'inventoryManagement': 'SHOPIFY',
                    'inventoryPolicy': 'DENY'
                }
            ]
        }
        
        # Add image if available
        if product_data.get('product_image'):
            product_input['images'] = [
                {'src': product_data['product_image']}
            ]
        
        variables = {'input': product_input}
        
        result = self._make_request(mutation, variables)
        
        if result and 'data' in result:
            data = result['data']['productCreate']
            
            if data['userErrors']:
                self.logger.error(f"Errors creating product: {data['userErrors']}")
                return None
            
            product_id = data['product']['id']
            self.logger.info(f"✓ Created: {data['product']['title']}")
            return product_id
        
        return None
    
    def find_product_by_sku(self, sku: str) -> Optional[str]:
        """Find product by SKU. Returns product ID if found."""
        query = """
        query($query: String!) {
            products(first: 1, query: $query) {
                edges {
                    node {
                        id
                        title
                    }
                }
            }
        }
        """
        
        variables = {'query': f'sku:{sku}'}
        result = self._make_request(query, variables)
        
        if result and 'data' in result:
            edges = result['data']['products']['edges']
            if edges:
                return edges[0]['node']['id']
        
        return None
    
    def update_product_price(self, product_id: str, variant_id: str, new_price: str) -> bool:
        """Update product variant price."""
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
        
        result = self._make_request(mutation, variables)
        
        if result and 'data' in result:
            data = result['data']['productVariantUpdate']
            if not data['userErrors']:
                self.logger.info(f"✓ Updated price: {new_price}")
                return True
            else:
                self.logger.error(f"Errors: {data['userErrors']}")
        
        return False
    
    def sync_from_csv(self, csv_file: str, max_products: int = None) -> Dict[str, int]:
        """
        Sync products from CSV file.
        Returns statistics.
        """
        stats = {'created': 0, 'updated': 0, 'failed': 0, 'skipped': 0}
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                products = list(reader)
            
            total = len(products) if not max_products else min(len(products), max_products)
            self.logger.info(f"Syncing {total} products from {csv_file}")
            
            for i, product_data in enumerate(products[:max_products] if max_products else products, 1):
                self.logger.info(f"[{i}/{total}] {product_data.get('name', 'Unknown')}")
                
                # Check if product exists
                sku = product_data.get('article_number')
                if sku:
                    existing_id = self.find_product_by_sku(sku)
                    
                    if existing_id:
                        # Product exists - skip for now (updating is complex)
                        stats['skipped'] += 1
                        self.logger.info("  → Already exists, skipping")
                    else:
                        # Create new product
                        if self.create_product(product_data):
                            stats['created'] += 1
                        else:
                            stats['failed'] += 1
                else:
                    self.logger.warning("  → No SKU, skipping")
                    stats['skipped'] += 1
                
                # Rate limiting (2 requests/second)
                time.sleep(0.6)
            
            self.logger.info(f"Sync complete: {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error syncing: {e}")
            return stats
    
    def _format_price(self, price_str: str) -> str:
        """Format price for Shopify (decimal format)."""
        if not price_str:
            return "0.00"
        try:
            return f"{float(price_str.replace(',', '.')):.2f}"
        except:
            return "0.00"
    
    def _build_description(self, product: Dict) -> str:
        """Build HTML description."""
        parts = []
        
        if product.get('name'):
            parts.append(f"<p>{product['name']}</p>")
        
        parts.append("<ul>")
        if product.get('manufacturer'):
            parts.append(f"<li><strong>Manufacturer:</strong> {product['manufacturer']}</li>")
        if product.get('article_number'):
            parts.append(f"<li><strong>Article Number:</strong> {product['article_number']}</li>")
        if product.get('ean'):
            parts.append(f"<li><strong>EAN:</strong> {product['ean']}</li>")
        parts.append("</ul>")
        
        if product.get('product_url'):
            parts.append(f"<p><a href='{product['product_url']}'>View original</a></p>")
        
        return "".join(parts)


def main():
    """Test the integration."""
    import sys
    
    # You need to provide shop URL and access token
    shop_url = "tbbt.myshopify.com"  # or tbbt.de
    access_token = "YOUR_ACCESS_TOKEN_HERE"
    
    if access_token == "YOUR_ACCESS_TOKEN_HERE":
        print("❌ Please configure your access token first")
        print("\nGet it from: Shopify Admin → Settings → Apps → Develop apps")
        print("Then update this script with your token")
        return
    
    integration = ShopifyGraphQLIntegration(shop_url, access_token)
    
    # Test connection
    if not integration.test_connection():
        print("❌ Connection failed")
        return
    
    # Sync products if CSV provided
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        max_products = int(sys.argv[2]) if len(sys.argv) > 2 else None
        
        stats = integration.sync_from_csv(csv_file, max_products)
        print(f"\nResults: {stats}")


if __name__ == "__main__":
    main()
