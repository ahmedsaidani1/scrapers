# Shopify CSV Import Guide (No API Needed!)

Since Shopify deprecated custom apps on January 1st, 2025, the easiest solution is to use **CSV import** which is built into Shopify.

## How It Works

1. **Convert** scraped data to Shopify CSV format
2. **Import** CSV files directly in Shopify admin
3. **Review** products before publishing
4. **Update** prices by re-importing with updated CSVs

## Step 1: Convert Scraped Data to Shopify Format

```bash
# Convert all scrapers to Shopify CSV format
python shopify_csv_export.py

# Or with 20% price markup
python shopify_csv_export.py 20
```

This creates CSV files in `shopify_imports/` folder:
```
shopify_imports/
  ├── heima24_shopify.csv
  ├── meinhausshop_shopify.csv
  ├── wolfonlineshop_shopify.csv
  └── ... (all your scrapers)
```

## Step 2: Import to Shopify

### Via Shopify Admin (Web Interface)

1. Go to **Shopify Admin** → **Products**
2. Click **Import** button (top right)
3. Click **Add file** and select a CSV from `shopify_imports/`
4. Click **Upload and continue**
5. Review the import preview
6. Click **Import products**
7. Wait for import to complete

### Import Settings

- **Overwrite existing products**: Check this to update prices
- **Match by**: SKU (recommended) or Barcode (EAN)

## Step 3: Review Products

After import:
1. Products are created as **drafts** (not published)
2. Go to Products → All products
3. Review product details, images, prices
4. Publish products when ready

## Updating Prices

To update prices for existing products:

1. Run scrapers to get latest data
2. Convert to Shopify CSV: `python shopify_csv_export.py`
3. Import CSV with **"Overwrite existing products"** checked
4. Shopify will match by SKU and update prices

## Automation

### Weekly Price Updates

Add to your cron job or Windows Task:

```bash
# After scrapers run
python shopify_csv_export.py 20
```

Then manually import the CSVs once a week, or use Shopify's bulk import API (requires Shopify Plus).

## Alternative: Use Shopify App

If you want automatic sync, you can use a third-party app from Shopify App Store:

### Recommended Apps:

1. **Matrixify (Excelify)** - Powerful import/export
   - Supports scheduled imports
   - Can import from URL
   - ~$30/month

2. **Bulk Product Edit** - Bulk operations
   - CSV import/export
   - Price updates
   - ~$10/month

3. **EZ Importer** - Simple CSV imports
   - Scheduled imports
   - Auto-updates
   - ~$20/month

### Setup with App:

1. Install app from Shopify App Store
2. Configure to import from CSV files
3. Set up scheduled imports (if supported)
4. Point to your `shopify_imports/` folder

## CSV Format Details

The exported CSV includes:
- Product title, description, vendor
- SKU, EAN/barcode
- Prices (with optional markup)
- Images
- Categories/tags
- Inventory settings

All fields are in Shopify's required format.

## Price Markup

Add markup when converting:

```bash
# 20% markup
python shopify_csv_export.py 20

# 15% markup
python shopify_csv_export.py 15

# No markup
python shopify_csv_export.py
```

## Batch Import Multiple Scrapers

The script automatically converts all CSV files in `data/` folder:

```bash
python shopify_csv_export.py 20
```

Output:
```
Converting heima24...
✓ Converted 150 products
✓ Saved to: shopify_imports/heima24_shopify.csv

Converting meinhausshop...
✓ Converted 200 products
✓ Saved to: shopify_imports/meinhausshop_shopify.csv

...

Conversion complete!
Files created: 10
```

## Import Limits

Shopify CSV import limits:
- **Max file size**: 15 MB
- **Max products per file**: ~5,000
- **Import time**: ~1-5 minutes per file

If you have more products, the script will split them automatically.

## Troubleshooting

### "Invalid CSV format"
- Make sure you're using the `_shopify.csv` files from `shopify_imports/`
- Don't modify the CSV headers

### "Products not updating"
- Check "Overwrite existing products" during import
- Verify SKUs match between CSV and existing products

### "Images not importing"
- Image URLs must be publicly accessible
- Check that `product_image` field has valid URLs

### "Prices wrong"
- Check price markup setting
- Verify German format (comma) is converted correctly

## Comparison: CSV vs API

| Feature | CSV Import | API (deprecated) |
|---------|-----------|------------------|
| Setup | Easy | Complex |
| Cost | Free | Free |
| Automation | Manual/App | Automatic |
| Speed | Slow (manual) | Fast |
| Updates | Re-import | Real-time |
| Availability | ✅ Always | ❌ Deprecated |

## Recommended Workflow

**Weekly Schedule:**

1. **Sunday 00:00** - Scrapers run automatically
2. **Sunday 00:30** - Convert to Shopify CSV
3. **Monday morning** - Import CSVs to Shopify (5 minutes)
4. **Review** - Check products, publish new ones

**Or use a Shopify app for automatic imports**

## Summary

✅ **Pros:**
- No API needed
- Works with all Shopify plans
- Simple and reliable
- Built-in Shopify feature

⚠️ **Cons:**
- Manual import step (unless using app)
- Not real-time
- Requires weekly maintenance

For most use cases, CSV import is the best solution after the API deprecation!
