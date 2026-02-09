# Shopify API Integration - Setup Complete ✓

## Overview
Successfully integrated Shopify API using OAuth 2.0 Client Credentials (2026+ method) to automatically sync products from scraped data.

## What Was Done

### 1. OAuth 2.0 Client Credentials Setup
- Created app in Shopify Dev Dashboard
- Obtained credentials:
  - Client ID: `ada83e69c6faef1b60afbed47019aabd`
  - Client Secret: `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`
  - Store: m13kjy-se.myshopify.com (API domain)
  - Primary domain: tbbt.de

### 2. Created Integration Script
- **File**: `shopify_api_integration.py`
- **Features**:
  - OAuth 2.0 token exchange with auto-refresh (24hr expiry)
  - GraphQL Admin API using `productSet` mutation
  - Handles multiple CSV column name formats
  - Creates products as DRAFT status
  - Includes SKU, EAN/barcode, price, images
  - Truncates long product types (255 char limit)
  - Validates image URLs
  - Rate limiting: 0.6s delay between requests

### 3. Configuration
- **File**: `shopify_config.py`
- OAuth credentials stored
- API version: 2024-10
- Price markup: disabled (can be enabled)
- Products created as DRAFT for review

## Test Results
✓ **67 products created successfully** from 15 CSV files
✓ Only 1 failure (invalid image URL with spaces)
✓ Connection test passed
✓ Token exchange working
✓ Products visible in Shopify admin

## How to Use

### Manual Sync
```bash
# Sync 10 products per file (testing)
python shopify_api_integration.py 10

# Sync all products
python shopify_api_integration.py
```

### Weekly Automation
Create Windows scheduled task to run every Sunday at 5:00 AM (after scrapers finish at 2 AM):

```powershell
schtasks /create /tn "Weekly_Shopify_API_Sync" /tr "python C:\Users\ahmed\Desktop\scrapers\shopify_api_integration.py" /sc weekly /d SUN /st 05:00 /ru "SYSTEM"
```

## Product Flow
1. **Sunday 2:00 AM**: Scrapers run → Update `data/*.csv`
2. **Sunday 5:00 AM**: Shopify API sync → Create products as DRAFT
3. **Manual Review**: Review products in Shopify admin
4. **Publish**: Manually publish approved products

## API Scopes Required
- `read_products`
- `write_products`
- `read_inventory`
- `write_inventory`

## Rate Limits
- GraphQL: 2 requests/second
- Current delay: 0.6s per product (safe)
- Token valid: 24 hours (auto-refreshes)

## Product Data Mapping
| CSV Column | Shopify Field |
|------------|---------------|
| product_name / name / Title | title |
| price / price_gross / Variant Price | price |
| sku / article_number / Variant SKU | sku |
| ean / Variant Barcode | barcode |
| product_image / Image Src | image |
| manufacturer / Vendor | vendor |
| category / Type | productType |
| description | descriptionHtml |

## Troubleshooting

### Token Issues
- Tokens expire after 24 hours
- Script auto-refreshes tokens
- Check credentials in `shopify_config.py`

### Product Creation Fails
- Check product type length (<255 chars) ✓ Fixed
- Validate image URLs (must start with http) ✓ Fixed
- Ensure price is valid number

### Rate Limiting
- Increase delay in code if hitting limits
- Current: 0.6s per product

## Next Steps
1. ✓ Test integration (DONE - 67 products created)
2. Set up weekly automation task
3. Monitor first automated run
4. Review and publish products in Shopify admin

## Files Modified
- `shopify_api_integration.py` - Main integration script
- `shopify_config.py` - OAuth credentials and config

## Success Metrics
- ✓ 67/68 products created (98.5% success rate)
- ✓ OAuth token exchange working
- ✓ GraphQL API calls successful
- ✓ Products created as DRAFT
- ✓ Images, SKUs, prices all synced

---
**Status**: READY FOR PRODUCTION
**Last Updated**: February 3, 2026
