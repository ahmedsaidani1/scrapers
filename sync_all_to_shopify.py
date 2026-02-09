"""
Batch sync all scraped products to Shopify
"""
import glob
import sys
from shopify_integration import ShopifyIntegration


def sync_all_scrapers(max_per_scraper: int = None, test_mode: bool = False):
    """
    Sync all CSV files from data/ directory to Shopify.
    
    Args:
        max_per_scraper: Maximum products per scraper (None = all)
        test_mode: If True, only sync 5 products per scraper for testing
    """
    integration = ShopifyIntegration()
    
    # Validate configuration
    if not integration.validate_config():
        print("\n❌ Configuration incomplete. Please update shopify_config.py")
        print("See SHOPIFY_INTEGRATION_SETUP.md for instructions")
        return
    
    # Test connection
    print("Testing Shopify connection...")
    if not integration.test_connection():
        print("❌ Connection failed. Check your credentials.")
        return
    
    print("\n" + "="*60)
    print("Batch Sync to Shopify")
    print("="*60)
    
    # Get all CSV files
    csv_files = glob.glob('data/*.csv')
    
    if not csv_files:
        print("\n⚠ No CSV files found in data/ directory")
        print("Run scrapers first to generate data")
        return
    
    # Apply test mode limit
    if test_mode:
        max_per_scraper = 5
        print(f"\n⚠ TEST MODE: Only syncing {max_per_scraper} products per scraper")
    
    print(f"\nFound {len(csv_files)} CSV files to sync")
    
    if max_per_scraper:
        print(f"Limit: {max_per_scraper} products per file")
    
    # Confirm before proceeding
    if not test_mode:
        response = input("\nProceed with sync? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Sync cancelled")
            return
    
    # Sync each file
    total_stats = {'created': 0, 'updated': 0, 'failed': 0, 'skipped': 0}
    
    for i, csv_file in enumerate(csv_files, 1):
        scraper_name = csv_file.replace('data/', '').replace('.csv', '')
        
        print(f"\n[{i}/{len(csv_files)}] Syncing {scraper_name}...")
        print("-" * 60)
        
        try:
            stats = integration.sync_from_csv(csv_file, max_per_scraper)
            
            # Update totals
            for key in total_stats:
                total_stats[key] += stats[key]
            
            print(f"  Created: {stats['created']}")
            print(f"  Updated: {stats['updated']}")
            print(f"  Failed: {stats['failed']}")
            print(f"  Skipped: {stats['skipped']}")
            
        except Exception as e:
            print(f"  ✗ Error syncing {scraper_name}: {e}")
            total_stats['failed'] += 1
    
    # Final summary
    print("\n" + "="*60)
    print("Sync Complete - Total Results")
    print("="*60)
    print(f"  Products Created: {total_stats['created']}")
    print(f"  Products Updated: {total_stats['updated']}")
    print(f"  Products Failed: {total_stats['failed']}")
    print(f"  Products Skipped: {total_stats['skipped']}")
    print(f"  Total Processed: {sum(total_stats.values())}")
    print("="*60)
    
    if test_mode:
        print("\n✓ Test sync complete!")
        print("Review products in Shopify admin, then run without --test flag")
    else:
        print("\n✓ Full sync complete!")
        print("Review products in Shopify admin before publishing")


def main():
    """Main execution."""
    test_mode = '--test' in sys.argv
    
    # Get max products from command line
    max_per_scraper = None
    for arg in sys.argv[1:]:
        if arg.isdigit():
            max_per_scraper = int(arg)
            break
    
    sync_all_scrapers(max_per_scraper, test_mode)


if __name__ == "__main__":
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python sync_all_to_shopify.py [OPTIONS]")
        print("\nOptions:")
        print("  --test          Test mode (only 5 products per scraper)")
        print("  [NUMBER]        Max products per scraper (e.g., 50)")
        print("  --help, -h      Show this help message")
        print("\nExamples:")
        print("  python sync_all_to_shopify.py --test")
        print("  python sync_all_to_shopify.py 50")
        print("  python sync_all_to_shopify.py")
    else:
        main()
