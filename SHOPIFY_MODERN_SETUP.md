# Modern Shopify Integration Setup

This guide follows the latest Shopify Dev Dashboard best practices for creating API-only apps.

## Overview

Based on [Shopify's official documentation](https://shopify.dev/docs/apps/build/dev-dashboard/create-apps-using-dev-dashboard), this integration uses:

- **OAuth 2.0 Client Credentials Grant** - Modern, secure authentication
- **App Versions** - Track configuration changes over time
- **Latest API Version** - Using 2024-10 or newer
- **GraphQL + REST** - Best of both APIs

## Step-by-Step Setup

### Step 1: Access Dev Dashboard

1. Log in to your Shopify admin: `https://tbbt.myshopify.com/admin`
2. Navigate to **Settings** (bottom left, gear icon)
3. Click **Apps and sales channels**
4. Click **Develop apps** (top right)

If you don't see "Develop apps":
- Click **"Allow custom app development"**
- Confirm the action

### Step 2: Create App via Dev Dashboard

1. Click **Create app** button
2. Select **Start from Dev Dashboard**
3. Enter app name: `Product Scraper Integration`
4. Click **Create**

### Step 3: Create App Version

From the **Versions** tab:

1. Click **Create version**
2. Configure the following:

   **App URL:**
   - If not embedded: Use `https://shopify.dev/apps/default-app-home`
   - If you have a server: Enter your app URL

   **Webhooks API version:**
   - Select the newest version (e.g., `2024-10`)

   **App scopes:**
   - ☑ `read_products`
   - ☑ `write_products`
   - ☑ `read_inventory`
   - ☑ `write_inventory`

3. Click **Release**

### Step 4: Install App

1. From your app's **Home** tab in Dev Dashboard
2. Scroll down and click **Install app**
3. Select your store: `tbbt.myshopify.com`
4. Click **Install**
5. Review and approve the permissions

### Step 5: Get Client Credentials

After installation:

1. Go to **API credentials** tab
2. You'll see:
   - **Client ID** (similar to API key)
   - **Client secret** (click to reveal)

⚠️ **IMPORTANT:** Copy both values immediately and store securely.

### Step 6: Update Configuration

Update `shopify_config.py`:

```python
SHOPIFY_CONFIG = {
    # Your Shopify store URL
    'shop_url': 'tbbt.myshopify.com',
    
    # OAuth 2.0 credentials (from Dev Dashboard)
    'client_id': 'your-client-id-here',
    'client_secret': 'your-client-secret-here',
    
    # API version (use latest)
    'api_version': '2024-10',
    
    # Authentication method
    'auth_method': 'oauth',  # Use OAuth 2.0
    
    # ... rest of config
}
```

### Step 7: Test Connection

```bash
python shopify_oauth_integration.py
```

Expected output:
```
✓ Successfully obtained access token
✓ Successfully connected to Shopify store: TBBT
✓ Connection successful!
```

## Key Differences from Old Method

### Old Method (Basic Auth)
```python
# Direct API key/password in URL
base_url = f"https://{api_key}:{password}@{shop_url}/admin/api/{version}"
```

### New Method (OAuth 2.0)
```python
# Get access token first
token = get_access_token(client_id, client_secret)

# Use token in headers
headers = {'X-Shopify-Access-Token': token}
```

## Benefits of Modern Approach

1. **More Secure**
   - Tokens expire and refresh automatically
   - No credentials in URLs
   - Better audit trail

2. **Version Management**
   - Track scope changes over time
   - Roll back if needed
   - Easier to manage updates

3. **Better Performance**
   - Can use GraphQL for complex queries
   - More efficient data fetching
   - Reduced API calls

4. **Future-Proof**
   - Follows current Shopify standards
   - Compatible with new features
   - Better support from Shopify

## Usage Examples

### Test Connection
```bash
python shopify_oauth_integration.py
```

### Sync Products from CSV
```bash
# Test with 10 products
python shopify_oauth_integration.py data/heima24.csv 10

# Sync all products
python shopify_oauth_integration.py data/heima24.csv
```

### Use in Your Scripts
```python
from shopify_oauth_integration import ShopifyOAuthIntegration

integration = ShopifyOAuthIntegration()

if integration.validate_config():
    # Sync products
    stats = integration.sync_from_csv('data/products.csv')
    print(f"Results: {stats}")
```

## Updating App Scopes

When you need to add new permissions:

1. Go to Dev Dashboard → Your App
2. Click **Versions** tab
3. Click **Create version**
4. Update scopes
5. Click **Release**
6. **Important:** Merchants must manually approve new scopes in their admin

## Troubleshooting

### "Failed to get access token"

Check:
- Client ID and secret are correct
- Store URL format: `yourstore.myshopify.com`
- App is installed on the store

### "401 Unauthorized"

- Token may have expired (auto-refreshes)
- Check app scopes are approved
- Verify app is still installed

### "403 Forbidden"

- Missing required scope
- Create new version with updated scopes
- Reinstall app to approve new scopes

### Rate Limiting

- REST API: 2 requests/second
- GraphQL: 1000 points/second
- Integration includes automatic delays

## Migration from Old Integration

If you're currently using `shopify_integration.py`:

1. **Keep both files** during transition
2. **Test new integration** with small batch
3. **Compare results** to ensure consistency
4. **Switch gradually** scraper by scraper
5. **Remove old integration** once confident

### Quick Migration Script

```python
# Old way
from shopify_integration import ShopifyIntegration
old_integration = ShopifyIntegration()

# New way
from shopify_oauth_integration import ShopifyOAuthIntegration
new_integration = ShopifyOAuthIntegration()

# Both work the same way
stats = new_integration.sync_from_csv('data/products.csv', 10)
```

## Security Best Practices

1. **Never commit credentials**
   - Add `shopify_config.py` to `.gitignore`
   - Use environment variables in production

2. **Rotate credentials regularly**
   - Create new version with new credentials
   - Revoke old credentials after migration

3. **Monitor API usage**
   - Check Dev Dashboard for usage stats
   - Set up alerts for unusual activity

4. **Use minimal scopes**
   - Only request permissions you need
   - Review scopes periodically

## Next Steps

1. ✅ Create app in Dev Dashboard
2. ✅ Configure scopes and install
3. ✅ Get client credentials
4. ✅ Update config file
5. ✅ Test connection
6. 🔄 Test with small product batch
7. 🔄 Review products in Shopify admin
8. 🔄 Run full sync
9. 🔄 Automate with cron/scheduled tasks

## Resources

- [Shopify Dev Dashboard Docs](https://shopify.dev/docs/apps/build/dev-dashboard/create-apps-using-dev-dashboard)
- [OAuth Client Credentials](https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/client-credentials)
- [API Versioning](https://shopify.dev/docs/api/usage/versioning)
- [GraphQL Admin API](https://shopify.dev/docs/api/admin-graphql)

## Support

For issues with this integration:
- Check logs for detailed error messages
- Verify configuration in `shopify_config.py`
- Test connection with test script
- Review Dev Dashboard for app status

For Shopify API questions:
- Visit [Shopify Dev Docs](https://shopify.dev)
- Check [Community Forums](https://community.shopify.com/c/shopify-apis-and-sdks/bd-p/shopify-apis-and-technology)
