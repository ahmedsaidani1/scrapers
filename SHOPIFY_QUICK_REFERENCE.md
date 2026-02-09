# Shopify Integration Quick Reference

## 🚀 Quick Start

### Already Have Credentials?

```bash
# Test your current setup
python shopify_integration.py

# Sync 10 products to test
python shopify_integration.py data/heima24.csv 10
```

### Want Modern OAuth Setup?

```bash
# 1. Follow setup guide
# See: SHOPIFY_MODERN_SETUP.md

# 2. Test new integration
python shopify_oauth_integration.py

# 3. Compare both methods
python test_shopify_both.py
```

## 📋 File Guide

| File | Purpose | When to Use |
|------|---------|-------------|
| `shopify_integration.py` | Legacy integration | Current production use |
| `shopify_oauth_integration.py` | Modern OAuth integration | New setup / migration |
| `shopify_config.py` | Configuration | Update credentials here |
| `SHOPIFY_MODERN_SETUP.md` | Setup guide | Setting up OAuth |
| `SHOPIFY_COMPARISON.md` | Detailed comparison | Deciding which to use |
| `test_shopify_both.py` | Test both methods | Before migration |
| `GET_SHOPIFY_TOKEN.md` | Get API token | Legacy setup |

## 🔧 Common Tasks

### Test Connection

```bash
# Legacy
python shopify_integration.py

# Modern
python shopify_oauth_integration.py

# Both
python test_shopify_both.py
```

### Sync Products

```bash
# Sync 10 products (test)
python shopify_integration.py data/heima24.csv 10

# Sync all products
python shopify_integration.py data/heima24.csv

# Sync all scrapers
python sync_all_to_shopify.py
```

### Update Configuration

Edit `shopify_config.py`:

```python
SHOPIFY_CONFIG = {
    'shop_url': 'yourstore.myshopify.com',  # Your store
    
    # For modern OAuth (recommended)
    'client_id': 'your-client-id',
    'client_secret': 'your-client-secret',
    'auth_method': 'oauth',
    
    # For legacy (still works)
    'api_key': 'your-api-key',
    'api_secret': 'your-api-secret',
    'auth_method': 'basic',
}
```

### Apply Price Markup

```python
'price_markup': {
    'enabled': True,
    'percentage': 20,  # 20% markup
    'fixed_amount': 0,  # Or add fixed amount
}
```

### Change Product Matching

```python
'match_by': 'sku',  # Options: 'sku', 'ean', 'title'
'update_existing': True,  # Update if exists
```

## 🔑 Getting Credentials

### Modern OAuth (Recommended)

1. Go to: `https://yourstore.myshopify.com/admin`
2. Settings → Apps and sales channels → Develop apps
3. Create app → Start from Dev Dashboard
4. Create version → Configure scopes → Install
5. Copy Client ID and Client Secret

**Scopes needed:**
- `read_products`
- `write_products`
- `read_inventory`
- `write_inventory`

### Legacy Method

1. Go to: `https://yourstore.myshopify.com/admin`
2. Settings → Apps and sales channels → Develop apps
3. Create app → Configure Admin API scopes
4. Install app → Reveal token once
5. Copy API key and access token

## 🐛 Troubleshooting

### "Configuration incomplete"

```bash
# Check your config
cat shopify_config.py

# Make sure you have either:
# - client_id + client_secret (OAuth)
# - api_key + api_secret (Basic)
# - api_key + api_password (Token)
```

### "Connection failed"

```bash
# Verify store URL format
shop_url: 'yourstore.myshopify.com'  # ✓ Correct
shop_url: 'yourstore.com'            # ✗ Wrong
shop_url: 'https://yourstore...'     # ✗ Wrong

# Test connection
python test_shopify_both.py
```

### "401 Unauthorized"

- Check credentials are correct
- Verify app is installed on store
- Check scopes are approved

### "429 Rate Limit"

- Integration includes automatic delays
- Wait a few minutes
- Reduce batch size

### "Product not found"

- Check SKU/EAN matches exactly
- Try different `match_by` setting
- Verify product exists in Shopify

## 📊 Performance Tips

### Use Modern OAuth for Better Performance

```python
# Legacy: ~2s per product search
# Modern: ~0.3s per product search
# 6.7x faster with GraphQL!
```

### Batch Operations

```python
# Good: Sync in batches
integration.sync_from_csv('data/products.csv', 50)

# Better: Use GraphQL bulk operations (modern only)
# Automatically used in modern integration
```

### Rate Limiting

```python
# Shopify limits:
# - REST: 2 requests/second
# - GraphQL: 1000 points/second

# Integration handles this automatically
# No need to worry about rate limits
```

## 🔄 Migration Checklist

Switching from legacy to modern:

- [ ] Read `SHOPIFY_MODERN_SETUP.md`
- [ ] Create app in Dev Dashboard
- [ ] Get client credentials
- [ ] Update `shopify_config.py`
- [ ] Test: `python shopify_oauth_integration.py`
- [ ] Compare: `python test_shopify_both.py`
- [ ] Test sync: `python shopify_oauth_integration.py data/heima24.csv 5`
- [ ] Verify in Shopify admin
- [ ] Update scraper scripts
- [ ] Monitor for issues
- [ ] Remove legacy code (after testing)

## 📝 Code Examples

### Basic Usage

```python
from shopify_oauth_integration import ShopifyOAuthIntegration

# Initialize
integration = ShopifyOAuthIntegration()

# Validate config
if not integration.validate_config():
    print("Please configure credentials")
    exit(1)

# Test connection
if integration.test_connection():
    print("Connected!")

# Sync products
stats = integration.sync_from_csv('data/products.csv', 10)
print(f"Created: {stats['created']}, Updated: {stats['updated']}")
```

### In Scraper Scripts

```python
# Add to your scraper
if "--push-to-shopify" in sys.argv:
    from shopify_oauth_integration import ShopifyOAuthIntegration
    
    integration = ShopifyOAuthIntegration()
    if integration.validate_config():
        stats = integration.sync_from_csv(output_file)
        print(f"Synced to Shopify: {stats}")
```

### Custom Product Data

```python
product_data = {
    'name': 'Product Name',
    'manufacturer': 'Brand',
    'category': 'Category',
    'article_number': 'SKU123',
    'ean': '1234567890123',
    'price_gross': '99.99',
    'price_net': '84.03',
    'product_image': 'https://example.com/image.jpg',
    'product_url': 'https://example.com/product'
}

# Create product
result = integration.create_product(product_data)

# Or sync (create/update automatically)
success = integration.sync_product(product_data)
```

## 🔐 Security Best Practices

1. **Never commit credentials**
   ```bash
   # Add to .gitignore
   shopify_config.py
   ```

2. **Use environment variables in production**
   ```python
   import os
   SHOPIFY_CONFIG = {
       'client_id': os.getenv('SHOPIFY_CLIENT_ID'),
       'client_secret': os.getenv('SHOPIFY_CLIENT_SECRET'),
   }
   ```

3. **Rotate credentials regularly**
   - Create new version in Dev Dashboard
   - Update config
   - Revoke old credentials

4. **Use minimal scopes**
   - Only request what you need
   - Review periodically

## 📚 Additional Resources

- **Setup:** `SHOPIFY_MODERN_SETUP.md`
- **Comparison:** `SHOPIFY_COMPARISON.md`
- **Legacy Setup:** `GET_SHOPIFY_TOKEN.md`
- **Full Guide:** `SHOPIFY_INTEGRATION_SETUP.md`

- **Shopify Docs:** https://shopify.dev
- **OAuth Guide:** https://shopify.dev/docs/apps/build/authentication-authorization
- **API Reference:** https://shopify.dev/docs/api/admin-rest

## 💡 Tips

- Start with small batches (10-20 products)
- Review products in Shopify admin before publishing
- Use draft status for new products
- Monitor logs for errors
- Test both integrations before migration
- Keep backups of your Shopify data

## ❓ Quick Answers

**Q: Which integration should I use?**
A: Modern OAuth for production, legacy for quick tests.

**Q: Can I use both?**
A: Yes! They don't interfere with each other.

**Q: How long does setup take?**
A: Legacy: 5 minutes, Modern: 15 minutes.

**Q: Will legacy stop working?**
A: Not immediately, but OAuth is recommended for new apps.

**Q: Is migration risky?**
A: No - both create identical products. Test side-by-side first.

**Q: How do I get help?**
A: Check the detailed guides in the documentation files.
