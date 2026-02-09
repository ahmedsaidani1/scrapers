# Shopify Integration - Implementation Summary

## Overview

Implemented a complete Shopify integration system that allows scraped products to be automatically imported and updated in your Shopify store.

## What Was Created

### 1. Core Integration Module (`shopify_integration.py`)

**Features:**
- ✅ Connect to Shopify Admin API
- ✅ Create new products with all scraped data
- ✅ Update existing products (price updates)
- ✅ Smart product matching (by SKU, EAN, or title)
- ✅ Price markup support (percentage or fixed)
- ✅ Batch import from CSV files
- ✅ Rate limiting (respects Shopify's 2 req/sec limit)
- ✅ Error handling and logging
- ✅ Product image import
- ✅ Metafields for additional data (source URL, net price)

**Product Data Mapping:**
```
Scraped Data          → Shopify Field
─────────────────────────────────────
name/title            → Product Title
manufacturer          → Vendor
category              → Product Type
article_number        → SKU
ean                   → Barcode
price_gross           → Price (with markup)
price_net             → Metafield
product_image         → Product Image
product_url           → Metafield (source)
```

### 2. Configuration File (`shopify_config.py`)

**Settings:**
- Store URL and API credentials
- Price markup configuration
- Product matching strategy
- Default tags and publishing status
- Update behavior for existing products

**Security:**
- Added to `.gitignore` to protect credentials
- Template provided with placeholders

### 3. Batch Sync Script (`sync_all_to_shopify.py`)

**Features:**
- Sync all scrapers at once
- Test mode (5 products per scraper)
- Limit products per scraper
- Progress tracking
- Summary statistics
- Confirmation prompt for safety

**Usage:**
```bash
python sync_all_to_shopify.py --test      # Test with 5 products
python sync_all_to_shopify.py 50          # Limit to 50 per scraper
python sync_all_to_shopify.py             # Full sync
```

### 4. Test Scripts

**`test_shopify_connection.py`**
- Validates configuration
- Tests API connection
- Verifies permissions
- Provides troubleshooting guidance

**Individual scraper sync:**
```bash
python shopify_integration.py data/heima24.csv 10
```

### 5. Documentation

**`SHOPIFY_INTEGRATION_SETUP.md`** (Comprehensive)
- Prerequisites and requirements
- Step-by-step setup instructions
- Configuration options
- Usage examples
- Troubleshooting guide
- Best practices
- Security notes

**`SHOPIFY_QUICK_START.md`** (5-Minute Guide)
- Quick setup steps
- Common commands
- Basic troubleshooting
- Automation setup

## How It Works

### Product Creation Flow

1. **Read CSV** → Load scraped product data
2. **Match Existing** → Search Shopify for existing product (by SKU/EAN)
3. **Apply Markup** → Add configured price markup
4. **Create/Update** → Create new product or update existing
5. **Add Metadata** → Store source URL and additional data
6. **Rate Limit** → Wait 0.6s between requests
7. **Log Results** → Track success/failure

### Smart Matching

The integration can match products by:
- **SKU** (article_number) - Most reliable
- **EAN** (barcode) - Good for products with barcodes  
- **Title** - Fallback option

Configurable in `shopify_config.py`:
```python
'match_by': 'sku',  # or 'ean' or 'title'
```

### Price Markup

Optional markup can be applied:
```python
'price_markup': {
    'enabled': True,
    'percentage': 20,     # 20% markup
    'fixed_amount': 5.00  # Or add fixed amount
}
```

### Safety Features

1. **Unpublished by default** - Products created as drafts for review
2. **Test mode** - Sync only 5 products for testing
3. **Confirmation prompt** - Asks before full sync
4. **Error handling** - Continues on individual failures
5. **Detailed logging** - Track all operations

## Setup Requirements

### Shopify Side

1. Create a private app in Shopify admin
2. Enable API scopes: `read_products`, `write_products`, `read_inventory`, `write_inventory`
3. Get Admin API access token (starts with `shpat_`)

### Configuration

Update `shopify_config.py`:
```python
'shop_url': 'yourstore.myshopify.com',
'api_password': 'shpat_xxxxxxxxxxxxx',
```

### Dependencies

Already in `requirements.txt`:
- `requests>=2.31.0` ✅

## Usage Examples

### Test Connection
```bash
python test_shopify_connection.py
```

### Test Sync (Small Batch)
```bash
python sync_all_to_shopify.py --test
```

### Sync Specific Scraper
```bash
python shopify_integration.py data/heima24.csv 10
```

### Full Sync All Scrapers
```bash
python sync_all_to_shopify.py
```

### Automated Weekly Sync

Add to cron job (Linux/Mac):
```bash
# After scrapers run on Sunday
0 2 * * 0 cd /path/to/scrapers && python sync_all_to_shopify.py 50
```

Add to Windows Task Scheduler:
```powershell
# In setup_windows_task.ps1
python sync_all_to_shopify.py 50
```

## Integration with Existing Scrapers

### Option 1: Manual Sync After Scraping

```bash
# Run scrapers
python run_all_scrapers_sequential.py

# Then sync to Shopify
python sync_all_to_shopify.py 50
```

### Option 2: Auto-Sync Per Scraper

Modify individual scrapers to add `--push-to-shopify` flag:

```python
if "--push-to-shopify" in sys.argv:
    from shopify_integration import ShopifyIntegration
    integration = ShopifyIntegration()
    if integration.validate_config():
        stats = integration.sync_from_csv(scraper.get_output_file())
```

## Statistics and Reporting

After sync, you get detailed statistics:
```
Sync Results:
  Created: 45
  Updated: 12
  Failed: 2
  Skipped: 8
```

## Security Considerations

✅ **Implemented:**
- API credentials in separate config file
- Config file added to `.gitignore`
- Template provided without real credentials
- Documentation warns against committing credentials

⚠️ **Recommendations:**
- Rotate API tokens periodically
- Use environment variables in production
- Limit API permissions to minimum required
- Monitor API usage in Shopify admin

## Next Steps

1. **Setup** - Add your Shopify credentials to `shopify_config.py`
2. **Test** - Run `python test_shopify_connection.py`
3. **Small Batch** - Test with `python sync_all_to_shopify.py --test`
4. **Review** - Check products in Shopify admin
5. **Configure Markup** - Set your desired price markup
6. **Full Sync** - Run `python sync_all_to_shopify.py`
7. **Automate** - Add to weekly cron job/task scheduler
8. **Monitor** - Check logs and Shopify admin regularly

## Files Created

```
shopify_integration.py              # Core integration module
shopify_config.py                   # Configuration (add to .gitignore)
sync_all_to_shopify.py             # Batch sync script
test_shopify_connection.py         # Connection test
SHOPIFY_INTEGRATION_SETUP.md       # Full documentation
SHOPIFY_QUICK_START.md             # Quick start guide
SHOPIFY_INTEGRATION_SUMMARY.md     # This file
```

## API Rate Limits

Shopify limits:
- **2 requests per second**
- **40 requests per app per store** (burst)

The integration handles this automatically with 0.6s delays between requests.

## Troubleshooting

See `SHOPIFY_INTEGRATION_SETUP.md` for detailed troubleshooting guide.

Common issues:
- Configuration incomplete → Update `shopify_config.py`
- Connection failed → Check credentials and store URL
- Products not updating → Verify SKU/EAN matching
- Rate limit errors → Reduce batch size

## Success Criteria

✅ Products automatically imported to Shopify  
✅ Prices updated for existing products  
✅ Product images imported  
✅ Manufacturer and category data preserved  
✅ Source URLs stored for reference  
✅ Safe defaults (unpublished, review first)  
✅ Batch processing for efficiency  
✅ Error handling and logging  
✅ Test mode for safety  
✅ Comprehensive documentation  

## Conclusion

The Shopify integration is complete and ready to use. Follow the Quick Start guide to get up and running in 5 minutes, then use the full setup guide for advanced configuration and automation.
