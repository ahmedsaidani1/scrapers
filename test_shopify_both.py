"""
Test and compare both Shopify integration methods.
This helps you verify both work correctly before migration.
"""
import sys
import time
from shopify_integration import ShopifyIntegration
from shopify_oauth_integration import ShopifyOAuthIntegration


def test_integration(integration, name):
    """Test a Shopify integration."""
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print(f"{'='*60}")
    
    # Validate config
    print("\n1. Validating configuration...")
    if not integration.validate_config():
        print(f"   ❌ {name} configuration incomplete")
        return False
    print(f"   ✓ Configuration valid")
    
    # Test connection
    print("\n2. Testing connection...")
    if not integration.test_connection():
        print(f"   ❌ {name} connection failed")
        return False
    print(f"   ✓ Connection successful")
    
    # Test finding product (if SKU provided)
    if len(sys.argv) > 1:
        test_sku = sys.argv[1]
        print(f"\n3. Testing product search (SKU: {test_sku})...")
        start = time.time()
        product = integration.find_product_by_sku(test_sku)
        elapsed = time.time() - start
        
        if product:
            print(f"   ✓ Found product: {product.get('title', 'Unknown')}")
            print(f"   ⏱ Search took {elapsed:.2f}s")
        else:
            print(f"   ℹ Product not found (this is OK if it doesn't exist)")
            print(f"   ⏱ Search took {elapsed:.2f}s")
    
    print(f"\n✓ All {name} tests passed!")
    return True


def compare_performance():
    """Compare performance of both integrations."""
    if len(sys.argv) < 2:
        print("\nSkipping performance comparison (no SKU provided)")
        return
    
    test_sku = sys.argv[1]
    
    print(f"\n{'='*60}")
    print(f"Performance Comparison")
    print(f"{'='*60}")
    print(f"\nSearching for SKU: {test_sku}")
    print("Running 5 searches with each method...\n")
    
    # Test legacy
    legacy = ShopifyIntegration()
    if legacy.validate_config():
        legacy_times = []
        for i in range(5):
            start = time.time()
            legacy.find_product_by_sku(test_sku)
            elapsed = time.time() - start
            legacy_times.append(elapsed)
            time.sleep(0.6)  # Rate limiting
        
        legacy_avg = sum(legacy_times) / len(legacy_times)
        print(f"Legacy Integration:")
        print(f"  Average: {legacy_avg:.3f}s")
        print(f"  Min: {min(legacy_times):.3f}s")
        print(f"  Max: {max(legacy_times):.3f}s")
    
    # Test modern
    modern = ShopifyOAuthIntegration()
    if modern.validate_config():
        modern_times = []
        for i in range(5):
            start = time.time()
            modern.find_product_by_sku(test_sku)
            elapsed = time.time() - start
            modern_times.append(elapsed)
            time.sleep(0.6)  # Rate limiting
        
        modern_avg = sum(modern_times) / len(modern_times)
        print(f"\nModern Integration:")
        print(f"  Average: {modern_avg:.3f}s")
        print(f"  Min: {min(modern_times):.3f}s")
        print(f"  Max: {max(modern_times):.3f}s")
        
        if legacy.validate_config():
            improvement = ((legacy_avg - modern_avg) / legacy_avg) * 100
            print(f"\n📊 Modern is {improvement:.1f}% faster")


def main():
    """Main test function."""
    print("Shopify Integration Comparison Tool")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        print(f"Test SKU: {sys.argv[1]}")
    else:
        print("No SKU provided - will test connection only")
        print("Usage: python test_shopify_both.py [SKU]")
    
    # Test legacy integration
    legacy = ShopifyIntegration()
    legacy_ok = test_integration(legacy, "Legacy Integration")
    
    # Test modern integration
    modern = ShopifyOAuthIntegration()
    modern_ok = test_integration(modern, "Modern OAuth Integration")
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    
    if legacy_ok and modern_ok:
        print("✓ Both integrations working!")
        print("\nRecommendation: Use Modern OAuth Integration for production")
        print("See SHOPIFY_COMPARISON.md for details")
        
        # Performance comparison
        if len(sys.argv) > 1:
            compare_performance()
    elif legacy_ok:
        print("✓ Legacy integration working")
        print("⚠ Modern integration not configured yet")
        print("\nNext step: Follow SHOPIFY_MODERN_SETUP.md to set up OAuth")
    elif modern_ok:
        print("✓ Modern integration working")
        print("ℹ Legacy integration not configured (this is OK)")
    else:
        print("❌ Neither integration configured")
        print("\nNext steps:")
        print("1. For legacy: Update api_key/api_secret in shopify_config.py")
        print("2. For modern: Follow SHOPIFY_MODERN_SETUP.md")
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()
