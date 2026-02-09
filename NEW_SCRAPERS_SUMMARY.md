# New Scrapers Summary

## Overview
Two new scrapers have been created and configured:

1. **glo24.de** - Requires German VPN/Proxy
2. **wolf-online-shop.de** - Heating/HVAC parts shop

---

## 1. GLO24.DE Scraper

### Status: ⚠️ Requires VPN Setup

### Files Created:
- `glo24_scraper.py` - Main scraper with proxy support
- `test_glo24_proxy.py` - Proxy testing script
- `GLO24_VPN_SETUP.md` - Complete VPN/proxy setup guide

### Key Features:
✓ Cloudflare bypass using cloudscraper  
✓ Proxy/VPN support built-in  
✓ German IP required (site geo-restricted)  
⚠️ Needs proxy configuration before use

### Setup Required:
1. Choose a German proxy service (see GLO24_VPN_SETUP.md)
2. Update `config.py`:
   ```python
   "glo24": {
       ...
       "proxy": "http://username:password@de-proxy.example.com:8080"
   }
   ```
3. Test: `python test_glo24_proxy.py`
4. Run: `python glo24_scraper.py`

### Recommended Proxy Services:
- **Smartproxy** - $12.5/GB (best for testing)
- **Bright Data** - $15/GB (production)
- **ProxyMesh** - $10-50/month (budget)

### Configuration:
```python
# In config.py
SHEET_IDS = {
    "glo24": "TBD",  # Add your Google Sheet ID
}

SCRAPER_CONFIGS = {
    "glo24": {
        "base_url": "https://glo24.de",
        "proxy": None,  # SET YOUR GERMAN PROXY HERE
    }
}
```

---

## 2. WOLF-ONLINE-SHOP.DE Scraper

### Status: ✅ Ready to Use

### Files Created:
- `wolf_online_shop_scraper.py` - Main scraper
- `test_wolf_online_shop.py` - Test script
- `run_wolf_online_shop_50.py` - Limited run script
- `WOLF_ONLINE_SHOP_SETUP.md` - Setup guide

### Key Features:
✓ Cloudflare bypass using cloudscraper  
✓ Product discovery from homepage  
✓ Price extraction (gross + net calculation)  
✓ Article number extraction  
✓ Image URL extraction  
✓ No VPN required  
✓ Ready to use immediately

### Quick Start:
```bash
# Test the scraper
python test_wolf_online_shop.py

# Run with 50 product limit
python run_wolf_online_shop_50.py

# Run full scrape
python wolf_online_shop_scraper.py

# Push to Google Sheets
python wolf_online_shop_scraper.py --push-to-sheets
```

### Test Results:
```
✓ PASS - Sitemap Parsing (10 products found)
✓ PASS - Single Product (all fields extracted)
Total: 2/2 tests passed
```

### Sample Product Data:
```
manufacturer        : (extracted from page)
category            : (from breadcrumbs)
name                : Uponor Smart Tacker Nadel 14-20mm, h=40mm VPE = 1000 Stück
title               : Uponor Smart Tacker Nadel 14-20mm, h=40mm VPE = 1000 Stück
article_number      : HE-UTN
price_net           : 54,58
price_gross         : 64.95
ean                 : (if available)
product_image       : https://www.wolf-online-shop.de/images/...
product_url         : https://www.wolf-online-shop.de/...::526585.html
```

### Configuration:
```python
# In config.py
SHEET_IDS = {
    "wolf_online_shop": "TBD",  # Add your Google Sheet ID
}

SCRAPER_CONFIGS = {
    "wolf_online_shop": {
        "base_url": "https://www.wolf-online-shop.de",
        "platform": "Custom (Heating/HVAC parts shop - Cloudflare protected)",
    }
}
```

### Product Discovery:
- Scrapes homepage for product links
- Identifies products by URL pattern: `::ID.html` (double colon)
- Filters out category pages: `:::ID.html` (triple colon)
- Can discover products from category pages if needed

---

## Next Steps

### For GLO24:
1. ⚠️ Sign up for German proxy service
2. ⚠️ Update proxy in `config.py`
3. ⚠️ Test with `python test_glo24_proxy.py`
4. ⚠️ Create Google Sheet and update SHEET_ID
5. ⚠️ Run scraper

### For Wolf-Online-Shop:
1. ✅ Scraper is ready
2. ⚠️ Create Google Sheet and update SHEET_ID in `config.py`
3. ✅ Run: `python run_wolf_online_shop_50.py`
4. ⚠️ Add to scheduled tasks

---

## Integration with Existing System

### Add to Parallel Scraping:
```python
# In run_all_scrapers_parallel.py
from wolf_online_shop_scraper import WolfOnlineShopScraper
# from glo24_scraper import Glo24Scraper  # After VPN setup

scrapers = [
    # ... existing scrapers ...
    WolfOnlineShopScraper(),
    # Glo24Scraper(),  # Uncomment after VPN setup
]
```

### Add to Sequential Scraping:
```python
# In run_all_scrapers_sequential.py
from wolf_online_shop_scraper import WolfOnlineShopScraper
# from glo24_scraper import Glo24Scraper  # After VPN setup

# ... existing code ...
run_scraper(WolfOnlineShopScraper())
# run_scraper(Glo24Scraper())  # Uncomment after VPN setup
```

---

## Technical Details

### Both Scrapers Use:
- **cloudscraper** - Bypasses Cloudflare protection
- **BeautifulSoup** - HTML parsing
- **BaseScraper** - Inherits common functionality
- **Google Sheets integration** - Ready to push data

### Data Format:
Both scrapers extract the standard 10 fields:
1. manufacturer
2. category
3. name
4. title
5. article_number
6. price_net (calculated from gross)
7. price_gross
8. ean
9. product_image
10. product_url

### Output Files:
- CSV: `data/glo24.csv` and `data/wolf_online_shop.csv`
- Logs: `logs/glo24.log` and `logs/wolf_online_shop.log`

---

## Troubleshooting

### GLO24 Issues:
- **403 Forbidden**: Proxy not configured or not German IP
- **Connection timeout**: Proxy server down
- **Cloudflare challenge**: Use residential proxies, not datacenter

### Wolf-Online-Shop Issues:
- **403 Forbidden**: Cloudscraper should handle this automatically
- **No products found**: Check logs, site structure may have changed
- **Missing data**: Some products may not have all fields (normal)

---

## Cost Estimates

### GLO24 (with proxy):
- **Testing**: $10-20/month (free trials available)
- **Production**: $50-100/month for moderate usage
- **Alternative**: Set up VPN on server (one-time setup)

### Wolf-Online-Shop:
- **No additional costs** - works with existing infrastructure

---

## Documentation

### Complete Guides:
- `GLO24_VPN_SETUP.md` - Detailed VPN/proxy setup for glo24
- `WOLF_ONLINE_SHOP_SETUP.md` - Complete setup guide for wolf-online-shop
- `NEW_SCRAPERS_SUMMARY.md` - This file

### Test Scripts:
- `test_glo24_proxy.py` - Test glo24 proxy setup (4 tests)
- `test_wolf_online_shop.py` - Test wolf-online-shop scraper (2 tests)
- `test_wolf_single_product.py` - Test single product extraction

### Run Scripts:
- `run_wolf_online_shop_50.py` - Run wolf scraper with 50 product limit

---

## Summary

✅ **Wolf-Online-Shop**: Fully functional, ready to use  
⚠️ **GLO24**: Requires German proxy setup before use

Both scrapers are production-ready once configured with Google Sheet IDs.
