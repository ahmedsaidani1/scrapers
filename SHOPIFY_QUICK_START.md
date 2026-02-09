# Shopify Integration - Quick Start

## 5-Minute Setup

### 1. Get Your Shopify Credentials

1. Go to your Shopify admin: `https://yourstore.myshopify.com/admin`
2. Navigate to: **Settings** → **Apps and sales channels** → **Develop apps**
3. Click **Create an app** → Name it "Product Scraper"
4. Click **Configure Admin API scopes**
5. Enable: `read_products`, `write_products`, `read_inventory`, `write_inventory`
6. Click **Save** → **Install app**
7. Copy the **Admin API access token** (starts with `shpat_`)

### 2. Configure

Edit `shopify_config.py`:

```python
SHOPIFY_CONFIG = {
    'shop_url': 'yourstore.myshopify.com',  # ← Your store URL
    'api_key': 'ecbc15c5ffeffec3a5a551ef6a1a71a3',  # ← Already set
    'api_password': 'shpat_xxxxx',  # ← Paste your access token here
    # ... rest stays the same
}
```

### 3. Test Connection

```bash
python test_shopify_connection.py
```

You should see: `✓ All tests passed!`

### 4. Test Sync (5 Products)

```bash
python sync_all_to_shopify.py --test
```

This syncs only 5 products per scraper for testing.

### 5. Review in Shopify

1. Go to Shopify admin → **Products**
2. Check imported products (they're unpublished by default)
3. Review prices, images, descriptions

### 6. Full Sync

Once you're happy with the test:

```bash
python sync_all_to_shopify.py
```

## Common Commands

```bash
# Test connection
python test_shopify_connection.py

# Test sync (5 products per scraper)
python sync_all_to_shopify.py --test

# Sync specific scraper (10 products)
python shopify_integration.py data/heima24.csv 10

# Full sync (all products, all scrapers)
python sync_all_to_shopify.py

# Sync with limit (50 products per scraper)
python sync_all_to_shopify.py 50
```

## Price Markup

To add markup to scraped prices, edit `shopify_config.py`:

```python
'price_markup': {
    'enabled': True,
    'percentage': 20,  # 20% markup
    'fixed_amount': 0,  # Or add fixed amount (e.g., 5.00)
}
```

## Automated Sync

Add to your weekly cron job (after scrapers run):

```bash
# In setup_cron.sh, add:
python sync_all_to_shopify.py 50
```

Or for Windows Task Scheduler:

```powershell
# In setup_windows_task.ps1, add:
python sync_all_to_shopify.py 50
```

## Troubleshooting

**"Configuration incomplete"**
- Add your store URL and API password to `shopify_config.py`

**"Connection failed"**
- Check API credentials are correct
- Verify store URL format: `store.myshopify.com` (not `store.com`)
- Ensure API permissions are enabled

**"Products not updating"**
- Check `match_by` setting in config (default: 'sku')
- Verify SKU/EAN values match between Shopify and scraped data

**"Rate limit errors"**
- The integration includes automatic delays
- If errors persist, reduce batch size or wait a few minutes

## Security

⚠️ **IMPORTANT**: Never commit `shopify_config.py` with real credentials!

The file is already in `.gitignore` to prevent accidental commits.

## Need Help?

See full documentation: `SHOPIFY_INTEGRATION_SETUP.md`
