"""
Export scraped data to Shopify-compatible CSV format
No API needed - just import the CSV file directly in Shopify admin
"""
import csv
import os
from typing import List, Dict
import glob


class ShopifyCSVExporter:
    """
    Export scraped product data to Shopify CSV format.
    The CSV can be imported directly via Shopify Admin > Products > Import
    """
    
    # Shopify CSV column headers (required format)
    SHOPIFY_HEADERS = [
        'Handle',
        'Title',
        'Body (HTML)',
        'Vendor',
        'Product Category',
        'Type',
        'Tags',
        'Published',
        'Option1 Name',
        'Option1 Value',
        'Variant SKU',
        'Variant Grams',
        'Variant Inventory Tracker',
        'Variant Inventory Policy',
        'Variant Fulfillment Service',
        'Variant Price',
        'Variant Compare At Price',
        'Variant Requires Shipping',
        'Variant Taxable',
        'Variant Barcode',
        'Image Src',
        'Image Position',
        'Image Alt Text',
        'Gift Card',
        'SEO Title',
        'SEO Description',
        'Variant Weight Unit',
        'Variant Tax Code',
        'Cost per item',
        'Status'
    ]
    
    def __init__(self, price_markup_percent: float = 0):
        """
        Initialize exporter.
        
        Args:
            price_markup_percent: Percentage markup to add (e.g., 20 for 20%)
        """
        self.price_markup = price_markup_percent
    
    def convert_to_shopify_format(self, scraped_data: List[Dict]) -> List[Dict]:
        """
        Convert scraped product data to Shopify CSV format.
        """
        shopify_products = []
        
        for product in scraped_data:
            # Generate handle (URL-friendly identifier)
            handle = self._generate_handle(product.get('name', ''))
            
            # Apply price markup
            price = self._apply_markup(product.get('price_gross', '0'))
            
            # Build HTML description
            body_html = self._build_description(product)
            
            # Create Shopify product row
            shopify_product = {
                'Handle': handle,
                'Title': product.get('name', product.get('title', '')),
                'Body (HTML)': body_html,
                'Vendor': product.get('manufacturer', ''),
                'Product Category': '',  # Leave empty for now
                'Type': product.get('category', ''),
                'Tags': 'imported, scraped',
                'Published': 'FALSE',  # Don't auto-publish (review first)
                'Option1 Name': 'Title',
                'Option1 Value': 'Default Title',
                'Variant SKU': product.get('article_number', ''),
                'Variant Grams': '0',
                'Variant Inventory Tracker': 'shopify',
                'Variant Inventory Policy': 'deny',
                'Variant Fulfillment Service': 'manual',
                'Variant Price': price,
                'Variant Compare At Price': '',
                'Variant Requires Shipping': 'TRUE',
                'Variant Taxable': 'TRUE',
                'Variant Barcode': product.get('ean', ''),
                'Image Src': product.get('product_image', ''),
                'Image Position': '1',
                'Image Alt Text': product.get('name', ''),
                'Gift Card': 'FALSE',
                'SEO Title': product.get('name', ''),
                'SEO Description': '',
                'Variant Weight Unit': 'kg',
                'Variant Tax Code': '',
                'Cost per item': product.get('price_net', ''),
                'Status': 'draft'
            }
            
            shopify_products.append(shopify_product)
        
        return shopify_products
    
    def export_csv(self, input_csv: str, output_csv: str = None) -> str:
        """
        Convert a scraped CSV to Shopify format.
        
        Args:
            input_csv: Path to scraped data CSV
            output_csv: Path for output (default: input_shopify.csv)
        
        Returns:
            Path to output CSV file
        """
        if not output_csv:
            base = os.path.splitext(input_csv)[0]
            output_csv = f"{base}_shopify.csv"
        
        # Read scraped data
        with open(input_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            scraped_data = list(reader)
        
        # Convert to Shopify format
        shopify_data = self.convert_to_shopify_format(scraped_data)
        
        # Write Shopify CSV
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.SHOPIFY_HEADERS)
            writer.writeheader()
            writer.writerows(shopify_data)
        
        print(f"✓ Converted {len(shopify_data)} products")
        print(f"✓ Saved to: {output_csv}")
        
        return output_csv
    
    def export_all_scrapers(self, output_dir: str = 'shopify_imports') -> List[str]:
        """
        Convert all scraped CSVs to Shopify format.
        
        Returns:
            List of output file paths
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all CSV files
        csv_files = glob.glob('data/*.csv')
        
        if not csv_files:
            print("⚠ No CSV files found in data/ directory")
            return []
        
        print(f"Converting {len(csv_files)} scrapers to Shopify format...\n")
        
        output_files = []
        
        for csv_file in csv_files:
            scraper_name = os.path.basename(csv_file).replace('.csv', '')
            output_file = os.path.join(output_dir, f"{scraper_name}_shopify.csv")
            
            print(f"Converting {scraper_name}...")
            
            try:
                self.export_csv(csv_file, output_file)
                output_files.append(output_file)
            except Exception as e:
                print(f"✗ Error converting {scraper_name}: {e}")
        
        print(f"\n{'='*60}")
        print(f"Conversion complete!")
        print(f"Output directory: {output_dir}/")
        print(f"Files created: {len(output_files)}")
        print(f"{'='*60}")
        
        return output_files
    
    def _generate_handle(self, title: str) -> str:
        """Generate URL-friendly handle from title."""
        import re
        # Convert to lowercase, replace spaces/special chars with hyphens
        handle = title.lower()
        handle = re.sub(r'[^a-z0-9]+', '-', handle)
        handle = handle.strip('-')
        return handle[:255]  # Shopify limit
    
    def _apply_markup(self, price_str: str) -> str:
        """Apply price markup."""
        if not price_str:
            return "0.00"
        
        try:
            # Convert German format to float
            price = float(price_str.replace(',', '.'))
            
            # Apply markup
            if self.price_markup > 0:
                price = price * (1 + self.price_markup / 100)
            
            return f"{price:.2f}"
        except:
            return "0.00"
    
    def _build_description(self, product: Dict) -> str:
        """Build product description HTML."""
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
        
        if product.get('category'):
            parts.append(f"<li><strong>Category:</strong> {product['category']}</li>")
        
        parts.append("</ul>")
        
        if product.get('product_url'):
            parts.append(f"<p><a href='{product['product_url']}' target='_blank'>View original product</a></p>")
        
        return "".join(parts)


def main():
    """Main execution."""
    import sys
    
    # Get price markup from command line (optional)
    price_markup = 0
    if len(sys.argv) > 1:
        try:
            price_markup = float(sys.argv[1])
            print(f"Applying {price_markup}% price markup\n")
        except:
            pass
    
    exporter = ShopifyCSVExporter(price_markup_percent=price_markup)
    
    # Convert all scrapers
    output_files = exporter.export_all_scrapers()
    
    if output_files:
        print("\n📋 Next Steps:")
        print("1. Go to Shopify Admin → Products")
        print("2. Click 'Import' button")
        print("3. Upload the CSV files from shopify_imports/ folder")
        print("4. Review imported products")
        print("5. Publish when ready")


if __name__ == "__main__":
    main()
