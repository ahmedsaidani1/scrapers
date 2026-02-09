# Wolf-Online-Shop Scraper Setup

## Overview
Scraper for **www.wolf-online-shop.de** - a German heating/HVAC parts online shop.

Website: https://www.wolf-online-shop.de  
Platform: Custom e-commerce platform  
Products: Heating systems, HVAC parts, Buderus, Junkers, Wolf brand parts

## Files Created

1. **wolf_online_shop_scraper.py** - Main scraper
2. **test_wolf_online_shop.py** - Test script
3. **run_wolf_online_shop_50.py** - Run with 50 product limit
4. **WOLF_ONLINE_SHOP_SETUP.md** - This file

## Quick Start

### 1. Test the Scraper
```bash
python test_wolf_online_shop.py
```

This will:
- Test category discovery
- Scrape a sample product
- Verify data extraction

### 2. Run Limited Scrape (50 products)
```bash
python run_wolf_online_shop_50.py
```

### 3. Run Full Scrape (1200+ products)
```bash
python wolf_online_shop_scraper.py
```

**Note**: Full scrape takes ~2-3 minutes as it crawls through 167 category pages.

### 4. Push to Google Sheets
```bash
python wolf_online_shop_scraper.py --push-to-sheets
```

## Configuration

### Update Google Sheet ID
Edit `config.py`:
```python
SHEET_IDS = {
    ...
    "wolf_online_shop": "YOUR_SHEET_ID_HERE",  # Replace TBD
}
```

### Scraper Settings
Already configured in `config.py`:
```python
"wolf_online_shop": {
    "base_url": "https://www.wolf-online-shop.de",
    "sitemap_url": "https://www.wolf-online-shop.de/sitemap.xml",
    "requires_login": False,
    "platform": "Custom (Heating/HVAC parts shop)",
    "custom_headers": {},
    "delay_override": None,
}
```

## Data Extracted

The scraper extracts the following fields:
- **manufacturer** - Brand/manufacturer name
- **category** - Product category
- **name** - Product name
- **title** - Product title
- **article_number** - Article/SKU number (Art.Nr.)
- **price_net** - Net price (calculated from gross)
- **price_gross** - Gross price (with 19% VAT)
- **ean** - EAN barcode
- **product_image** - Product image URL
- **product_url** - Product page URL

## Output

Data is saved to:
- **CSV**: `data/wolf_online_shop.csv`
- **Log**: `logs/wolf_online_shop.log`

## Features

✓ Category-based product discovery (167 categories)  
✓ Discovers 1200+ products automatically  
✓ Automatic price calculation (net from gross)  
✓ German VAT handling (19%)  
✓ Article number extraction  
✓ Image URL extraction  
✓ Category detection from breadcrumbs  
✓ Error handling and logging  
✓ Rate limiting to avoid blocking  
✓ Google Sheets integration ready  
✓ Cloudflare bypass using cloudscraper

## Site Characteristics

- **No login required** - Public product catalog
- **Cloudflare protected** - Uses cloudscraper to bypass
- **167 category pages** - Systematically crawled
- **1200+ products** - Full catalog discovery
- **German language** - All content in German
- **VAT included** - Prices shown with 19% VAT
- **Product URL pattern**: `/Product-Name::ID.html` (double colon)
- **Category URL pattern**: `/Category:::ID.html` (triple colon)

## Troubleshooting

### No products found
- Check if sitemap is accessible: https://www.wolf-online-shop.de/sitemap.xml
- Verify internet connection
- Check logs: `logs/wolf_online_shop.log`

### Missing data fields
- Some products may not have all fields (EAN, manufacturer, etc.)
- This is normal - scraper handles missing data gracefully

### Rate limiting / Blocking
- Scraper includes random delays (0.1-0.3 seconds)
- If blocked, increase delays in `config.py`:
  ```python
  MIN_DELAY = 0.5
  MAX_DELAY = 1.0
  ```

## Integration with Other Scrapers

Add to parallel scraping:
```python
# In run_all_scrapers_parallel.py
from wolf_online_shop_scraper import WolfOnlineShopScraper

scrapers = [
    # ... existing scrapers ...
    WolfOnlineShopScraper(),
]
```

Add to sequential scraping:
```python
# In run_all_scrapers_sequential.py
from wolf_online_shop_scraper import WolfOnlineShopScraper

# ... existing code ...
run_scraper(WolfOnlineShopScraper())
```

## Next Steps

1. ✓ Test scraper: `python test_wolf_online_shop.py`
2. ✓ Run limited scrape: `python run_wolf_online_shop_50.py`
3. ⚠ Create Google Sheet and update SHEET_ID in config.py
4. ⚠ Run full scrape: `python wolf_online_shop_scraper.py`
5. ⚠ Add to scheduled tasks (cron/Windows Task Scheduler)

## Notes

- Site appears to be accessible without VPN (unlike glo24.de)
- Products include heating systems, pumps, solar equipment, HVAC parts
- Brands: Wolf, Buderus, Junkers, Viessmann, Honeywell, and more
- Prices are in EUR with German VAT (19%)

## Support

Check logs for detailed error messages:
```bash
type logs\wolf_online_shop.log
```

For issues, verify:
1. Internet connection
2. Site is accessible: https://www.wolf-online-shop.de
3. Python dependencies installed: `pip install -r requirements.txt`
