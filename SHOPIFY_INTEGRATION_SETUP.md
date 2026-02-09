# Shopify Integration Setup Guide

This guide explains how to integrate your scraped products with Shopify.

## Overview

The Shopify integration allows you to:
- **Create new products** in your Shopify store from scraped data
- **Update existing products** (prices, inventory, etc.)
- **Match products** by SKU, EAN, or title
- **Apply price markup** (percentage or fixed amount)
- **Batch import** from CSV files
- **Auto-sync** after scraping runs

## Prerequisites

### 1. Shopify Store Access

You need admin access to your Shopify store.

### 2. Create a Private App (API Credentials)

1. Log in to your Shopify admin panel
2. Go to **Settings** → **Apps and sales channels**
3. Click **Develop apps** → **Create an app**
4. Name it "Product Scraper Integration"
5. Click **Configure Admin API scopes**
6. Enable these permissions:
   - `read_products`
   - `write_products`
   - `read_inventory`
   - `write_inventory`
7. Click **Save**
8. Click **Install app**
9. Copy your **Admin API access token** (this is your API password)

### 3. Get Your Store URL

Your store URL format: `yourstore.myshopify.com`

## Configuration

### Step 1: Update `shopify_config.py`

```python
SHOPIFY_CONFIG = {
    # Your Shopify store URL
    'shop_url': 'yourstore.myshopify.com',  # Replace with your actual store
    
    # API credentials
    'api_key': 'ecbc15c5ffeffec3a5a551ef6a1a71a3',  # Already configured
    'api_password': 'shpat_xxxxxxxxxxxxx',  # Add your Admin API access token
    
    # ... rest of config
}
```

### Step 2: Configure Price Markup (Optional)

If you want to add markup to scraped prices:

```python
'price_markup': {
    'enabled': True,
    'percentage': 20,  # 20% markup
    'fixed_amount': 0,  # Or add fixed amount
}
```

### Step 3: Configure Product Matching

Choose how to match existing products:

```python
'match_by': 'sku',  # Options: 'sku', 'ean', or 'title'
'update_existing': True,  # Update prices if product exists
```

## Usage

### Test Connection

```bash
python shopify_integration.py
```

This will test your API credentials and connection.

### Sync Products from CSV

```bash
# Sync all products from a scraper output
python shopify_integration.py data/heima24.csv

# Sync only first 10 products (for testing)
python shopify_integration.py data/heima24.csv 10
```

### Sync After Scraping

Add `--push-to-shopify` flag when running scrapers:

```bash
python heima24_scraper.py --max-products 50 --push-to-shopify
```

## Product Data Mapping

| Scraped Field | Shopify Field | Notes |
|---------------|---------------|-------|
| `name` / `title` | Product Title | Main product name |
| `manufacturer` | Vendor | Brand/manufacturer |
| `category` | Product Type | Product category |
| `article_number` | SKU | Unique identifier |
| `ean` | Barcode | EAN/GTIN code |
| `price_gross` | Price | With markup if configured |
| `price_net` | Metafield | Stored as custom field |
| `product_image` | Image | Main product image |
| `product_url` | Metafield | Source URL |

## Features

### 1. Smart Product Matching

The integration can find existing products by:
- **SKU** (article_number) - Most reliable
- **EAN** (barcode) - Good for products with barcodes
- **Title** - Fallback option

### 2. Update vs Create

- **New products**: Created with all data
- **Existing products**: Only price is updated (configurable)
- **Published status**: Products are unpublished by default (review first)

### 3. Rate Limiting

The integration respects Shopify's API rate limits:
- 2 requests per second
- Automatic delays between requests

### 4. Error Handling

- Failed products are logged
- Sync continues even if individual products fail
- Statistics provided at the end

## Batch Sync Script

Create `sync_all_to_shopify.py`:

```python
from shopify_integration import ShopifyIntegration
import glob

integration = ShopifyIntegration()

if not integration.validate_config():
    print("Please configure Shopify credentials first")
    exit(1)

# Sync all CSV files
csv_files = glob.glob('data/*.csv')

for csv_file in csv_files:
    print(f"\nSyncing {csv_file}...")
    stats = integration.sync_from_csv(csv_file, max_products=10)  # Test with 10 first
    print(f"Results: {stats}")
```

## Automated Sync

### Option 1: Add to Scraper Scripts

Modify your scraper to auto-sync:

```python
from shopify_integration import ShopifyIntegration

# After scraping
if "--push-to-shopify" in sys.argv:
    integration = ShopifyIntegration()
    if integration.validate_config():
        stats = integration.sync_from_csv(scraper.get_output_file())
        print(f"Shopify sync: {stats}")
```

### Option 2: Scheduled Sync

Add to your cron job or Windows Task:

```bash
# After scrapers run, sync to Shopify
python sync_all_to_shopify.py
```

## Troubleshooting

### Authentication Errors

- Verify your API access token is correct
- Check that the app has required permissions
- Ensure store URL format is correct (`store.myshopify.com`)

### Rate Limit Errors

- The integration includes automatic delays
- If you hit limits, reduce batch size
- Wait a few minutes and retry

### Products Not Updating

- Check `match_by` setting in config
- Verify SKU/EAN values match exactly
- Check `update_existing` is set to `True`

### Missing Data

- Some fields may be empty in scraped data
- Products will still be created with available data
- Review products in Shopify admin before publishing

## Best Practices

1. **Test First**: Always test with a small batch (10-20 products)
2. **Review Before Publishing**: Products are unpublished by default
3. **Backup**: Export your Shopify products before bulk imports
4. **Monitor**: Check logs for errors during sync
5. **Price Markup**: Set appropriate markup for your business
6. **Regular Updates**: Run scrapers weekly to keep prices current

## Security Notes

- **Never commit** `shopify_config.py` with real credentials to Git
- Add to `.gitignore`: `shopify_config.py`
- Use environment variables for production deployments
- Rotate API tokens periodically

## Support

For Shopify API documentation:
https://shopify.dev/docs/api/admin-rest

For issues with this integration:
- Check logs in console output
- Verify configuration in `shopify_config.py`
- Test connection with `python shopify_integration.py`
