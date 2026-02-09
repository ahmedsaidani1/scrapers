"""
Quick script to show Shopify import status and next steps.
"""
import os
import glob


def main():
    print("=" * 70)
    print("SHOPIFY CSV IMPORT - READY TO GO!")
    print("=" * 70)
    
    # Check for CSV files
    csv_files = glob.glob('shopify_imports/*_shopify.csv')
    
    if not csv_files:
        print("\n❌ No Shopify CSV files found!")
        print("\nRun this first:")
        print("  python shopify_csv_export.py")
        return
    
    print(f"\n✓ Found {len(csv_files)} Shopify CSV files ready to import")
    print(f"✓ Location: shopify_imports/ folder")
    
    # Count total products
    total_products = 0
    file_info = []
    
    for csv_file in sorted(csv_files):
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines()) - 1  # Subtract header
                total_products += lines
                
                name = os.path.basename(csv_file).replace('_shopify.csv', '')
                file_info.append((name, lines, csv_file))
        except:
            pass
    
    print(f"✓ Total products: {total_products:,}")
    
    # Show files
    print("\n" + "=" * 70)
    print("FILES READY TO IMPORT:")
    print("=" * 70)
    
    # Sort by product count
    file_info.sort(key=lambda x: x[1], reverse=True)
    
    for name, count, path in file_info:
        print(f"  {name:30s} {count:6,} products")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDED IMPORT ORDER:")
    print("=" * 70)
    
    print("\n1. TEST FIRST (small files):")
    for name, count, path in file_info:
        if count <= 20:
            print(f"   ✓ {name} ({count} products)")
    
    print("\n2. MEDIUM FILES:")
    for name, count, path in file_info:
        if 20 < count <= 500:
            print(f"   ✓ {name} ({count} products)")
    
    print("\n3. LARGE FILES (after testing):")
    for name, count, path in file_info:
        if count > 500:
            print(f"   ✓ {name} ({count:,} products)")
    
    # Instructions
    print("\n" + "=" * 70)
    print("HOW TO IMPORT:")
    print("=" * 70)
    
    print("\n1. Open Shopify Admin:")
    print("   https://admin.shopify.com/store/tbtgermany/products")
    
    print("\n2. Click 'Import' button (top right)")
    
    print("\n3. Upload CSV file from shopify_imports/ folder")
    
    print("\n4. Review and confirm import")
    
    print("\n5. Check imported products (they'll be in Draft status)")
    
    # Tips
    print("\n" + "=" * 70)
    print("TIPS:")
    print("=" * 70)
    
    print("\n✓ Start with small files to test")
    print("✓ Products are set to Draft (review before publishing)")
    print("✓ Shopify will skip duplicate SKUs automatically")
    print("✓ Large files may take several minutes to import")
    print("✓ You can import multiple files, one at a time")
    
    # Add markup option
    print("\n" + "=" * 70)
    print("NEED TO ADD PRICE MARKUP?")
    print("=" * 70)
    
    print("\nTo add 20% markup to all prices:")
    print("  python shopify_csv_export.py 20")
    
    print("\nThis will regenerate all CSV files with new prices.")
    
    print("\n" + "=" * 70)
    print("✓ Everything is ready! Start importing to Shopify.")
    print("=" * 70)


if __name__ == "__main__":
    main()
