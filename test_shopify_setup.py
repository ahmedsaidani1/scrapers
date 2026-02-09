"""
Quick test script for Shopify OAuth integration setup.
Run this after updating shopify_config.py with your credentials.
"""
from shopify_oauth_integration import ShopifyOAuthIntegration


def main():
    print("=" * 70)
    print("SHOPIFY OAUTH INTEGRATION - SETUP TEST")
    print("=" * 70)
    
    integration = ShopifyOAuthIntegration()
    
    # Step 1: Validate configuration
    print("\n[1/2] Validating configuration...")
    if not integration.validate_config():
        print("❌ Configuration incomplete!")
        print("\nPlease update shopify_config.py with:")
        print("  - client_id (from Shopify Dev Dashboard)")
        print("  - client_secret (from Shopify Dev Dashboard)")
        print("  - Make sure auth_method is set to 'oauth'")
        return False
    print("✓ Configuration valid")
    
    # Step 2: Test API connection (skip OAuth token for now)
    print("\n[2/2] Testing Shopify API connection...")
    if not integration.test_connection():
        print("❌ Connection test failed!")
        print("\nPossible issues:")
        print("  - App scopes not approved")
        print("  - Network connectivity issues")
        print("  - Store ID incorrect")
        return False
    
    # Success!
    print("\n" + "=" * 70)
    print("✓ SUCCESS! Shopify OAuth integration is working!")
    print("=" * 70)
    
    print("\n📋 Next Steps:")
    print("  1. Test syncing products:")
    print("     python shopify_oauth_integration.py data/heima24.csv 5")
    print("\n  2. Check products in Shopify admin:")
    print("     https://admin.shopify.com/store/tbtgermany/products")
    print("\n  3. Compare with legacy integration:")
    print("     python test_shopify_both.py")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
