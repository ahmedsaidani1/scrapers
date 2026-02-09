"""
Test Shopify API connection and credentials
"""
from shopify_integration import ShopifyIntegration


def test_connection():
    """Test Shopify API connection."""
    print("="*60)
    print("Shopify Connection Test")
    print("="*60)
    
    integration = ShopifyIntegration()
    
    # Step 1: Validate configuration
    print("\n1. Validating configuration...")
    if not integration.validate_config():
        print("   ✗ Configuration incomplete")
        print("\n   Please update shopify_config.py with:")
        print("   - shop_url: Your Shopify store URL (e.g., yourstore.myshopify.com)")
        print("   - api_password: Your Admin API access token")
        print("\n   See SHOPIFY_INTEGRATION_SETUP.md for detailed instructions")
        return False
    
    print("   ✓ Configuration valid")
    
    # Step 2: Test API connection
    print("\n2. Testing API connection...")
    if not integration.test_connection():
        print("   ✗ Connection failed")
        print("\n   Possible issues:")
        print("   - Incorrect API credentials")
        print("   - Store URL format wrong (should be: store.myshopify.com)")
        print("   - API permissions not configured")
        print("   - Network/firewall issues")
        return False
    
    print("   ✓ Connection successful")
    
    # Step 3: Test product search
    print("\n3. Testing product search...")
    try:
        # Try to find a product (will return None if no products exist)
        product = integration.find_product_by_sku("TEST_SKU_12345")
        print("   ✓ Product search working (no product found with test SKU, as expected)")
    except Exception as e:
        print(f"   ✗ Product search failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✓ All tests passed! Shopify integration is ready.")
    print("="*60)
    print("\nNext steps:")
    print("1. Test with a small batch: python shopify_integration.py data/heima24.csv 5")
    print("2. Review products in Shopify admin")
    print("3. Publish products when ready")
    print("4. Run full sync for all scrapers")
    
    return True


if __name__ == "__main__":
    test_connection()
