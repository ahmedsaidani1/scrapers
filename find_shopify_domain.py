"""
Helper script to find your correct Shopify domain.
"""
print("=" * 70)
print("FIND YOUR SHOPIFY DOMAIN")
print("=" * 70)

print("\nPlease check your Shopify admin and tell me:")
print("\n1. Go to: Settings → Domains")
print("   Look for 'Shopify domain' - it should be something like:")
print("   - xxxxx.myshopify.com")
print("   - store-name.myshopify.com")
print("")
print("2. OR look at your browser URL when in admin:")
print("   - If it shows: https://admin.shopify.com/store/XXXXX")
print("     Then your domain might be based on that store ID")
print("")
print("3. OR check the URL bar - it might show:")
print("   - https://yourstore.myshopify.com/admin")
print("")

print("\nCommon formats:")
print("  ✓ storename.myshopify.com")
print("  ✓ store-name.myshopify.com")
print("  ✗ storename.com (custom domain - won't work for API)")
print("  ✗ tbbt.de (custom domain - won't work for API)")

print("\n" + "=" * 70)
print("Once you find it, update shopify_config.py:")
print("  'shop_url': 'YOUR-STORE.myshopify.com'")
print("=" * 70)
