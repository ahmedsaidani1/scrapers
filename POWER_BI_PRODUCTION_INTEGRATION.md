# Power BI Production Integration

## Overview

Power BI data generation has been integrated into the production automation workflow. All scraped products are automatically pushed to a dedicated Power BI Google Sheet for real-time dashboard updates.

## What's Included

### 1. Automatic Data Collection
- All products from successful scrapers are combined into a single dataset
- Each product includes a `source` field identifying which scraper it came from
- Data is saved to `data/power_bi_test.csv`

### 2. Google Sheets Integration
- **Sheet ID**: `1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA`
- Automatically updated during production runs
- Contains all products from all scrapers with source attribution

### 3. Production Workflow

The production script (`run_production.py`) now includes 5 steps:

1. **Scrape Websites** - Run all configured scrapers
2. **Email Notifications** - Detect changes and send alerts
3. **Update Google Sheets** - Sync individual scraper sheets
4. **Generate Shopify CSV** - Create import files with markup
5. **Update Power BI Sheet** - Push combined data for dashboards ✨ NEW

## Running Production

### Manual Run
```bash
python run_production.py
```

### Test Mode (Limited Products)
```bash
python run_production.py 50
```

### Scheduled Run
The weekly automation (Sunday 00:00) automatically includes Power BI updates:
```powershell
# Setup the schedule (run as Administrator)
.\setup_production_schedule.ps1
```

## Power BI Dashboard Setup

### Step 1: Connect to Data Source
1. Open Power BI Desktop
2. Get Data → Web
3. Enter the Google Sheets URL for sheet ID: `1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA`

### Step 2: Load and Transform
- Power BI will automatically detect the CSV structure
- All columns are preserved including the `source` field
- Data refreshes automatically when the sheet is updated

### Step 3: Create Visualizations
Refer to these guides for dashboard creation:
- `POWER_BI_ARTICLE_SEARCH_GUIDE.md` - Article number search functionality
- `POWER_BI_COMPLETE_SOLUTION.md` - Complete dashboard setup
- `POWER_BI_QUICK_REFERENCE.md` - Quick tips and tricks

## Data Structure

The Power BI sheet contains all standard product fields plus:

| Field | Description |
|-------|-------------|
| article_number | Product SKU/ID |
| name | Product name |
| price | Current price |
| availability | Stock status |
| url | Product URL |
| image_url | Product image |
| ean | EAN barcode |
| manufacturer | Brand name |
| **source** | Scraper name (e.g., "meinhausshop", "heima24") |

## Benefits

✅ **Real-time Updates** - Data refreshes weekly with production runs
✅ **Multi-source Analysis** - Compare products across all scrapers
✅ **Automated Pipeline** - No manual data export needed
✅ **Historical Tracking** - Combined with snapshots for trend analysis
✅ **Dashboard Ready** - Pre-formatted for Power BI consumption

## Monitoring

Check the production logs for Power BI update status:
```
========================================
STEP 5: UPDATING POWER BI SHEET
========================================
  ✓ meinhausshop: 150 products
  ✓ heima24: 200 products
  ...
✓ Created combined CSV with 1500 products
✓ Successfully pushed 1500 products to Power BI Sheet
  Sheet ID: 1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA
```

## Troubleshooting

### Power BI Update Failed
- Check Google Sheets credentials in `credentials/credentials.json`
- Verify sheet ID is correct
- Ensure network connectivity

### Missing Products
- Check individual scraper logs in `logs/`
- Verify CSV files exist in `data/`
- Review scraper success status in production summary

### Data Not Refreshing in Power BI
- Refresh the data source in Power BI Desktop
- Check the Google Sheet was actually updated
- Verify the sheet URL is correct

## Related Files

- `run_production.py` - Main production script with Power BI integration
- `run_power_bi_test.py` - Standalone Power BI data generator
- `push_to_powerbi_sheet.py` - Direct sheet update utility
- `setup_production_schedule.ps1` - Automated scheduling setup

## Next Steps

1. Run production to populate the Power BI sheet
2. Connect Power BI Desktop to the Google Sheet
3. Create your dashboards using the guides
4. Set up automatic refresh in Power BI Service (optional)

---

**Last Updated**: February 2026
**Status**: ✅ Production Ready
