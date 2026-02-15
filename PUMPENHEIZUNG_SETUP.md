# Pumpenheizung Scraper Setup

## Website Information
- **URL**: https://pumpen-heizung.de
- **Company**: Metallhandel Jobst
- **Platform**: JTL Shop 5
- **Status**: ✅ WORKING

## Technical Details

### Challenges
1. **Very Slow Load Times**: Website takes 25-30+ seconds to load
2. **JavaScript Required**: Products are loaded dynamically
3. **Anti-Bot Protection**: Requires undetected-chromedriver

### Solution
- Uses **Selenium** with **undetected-chromedriver**
- Extracts products from homepage featured products section
- Headless mode for production deployment
- 120-second page load timeout

## Scraper Features

### Data Extracted
- ✅ Product Name (from schema.org markup)
- ✅ Price (from schema.org `itemprop="price"`)
- ✅ Article Number / SKU
- ✅ Manufacturer (from schema.org `itemprop="brand"`)
- ✅ Availability (from schema.org `itemprop="availability"`)
- ✅ Description
- ✅ Product URL

### Performance
- **Homepage Load**: ~3-5 seconds
- **Product Page Load**: ~4-5 seconds per product
- **10 Products**: ~1 minute total
- **50 Products**: ~5 minutes total

## Usage

### Test with 10 Products
```bash
python test_pumpenheizung.py
```

### Run with Custom Limit
```python
from pumpenheizung_scraper import PumpenheizungScraper

scraper = PumpenheizungScraper()
count = scraper.run(max_products=50)
print(f"Scraped {count} products")
```

### Run Unlimited (Production)
```python
from pumpenheizung_scraper import PumpenheizungScraper

scraper = PumpenheizungScraper()
count = scraper.run(max_products=None)  # Scrape ALL products
```

## Output

### CSV File
- **Location**: `data/pumpenheizung.csv`
- **Format**: Standard CSV with headers
- **Encoding**: UTF-8

### Sample Output
```csv
manufacturer,category,name,title,article_number,price_net,price_gross,ean,product_image,product_url
Wolf,,"Wolf - 2486462 - Wärmepumpe FHS-180-S-230V-e2-M2 Speicherinhalt 180 L, R290, 2.136,85 €",,2486462,,"2136,85",,,
IMI Hydronic,,"Heimeier - 2001-02.300 - Thermostat-Oberteil, 14,13 €",,2001-02.300,,"14,13",,,
```

## Production Integration

### Added to Production Pipeline
The scraper is now included in `run_production_powerbi.py`:
- **Position**: 9th out of 10 scrapers
- **Order**: Runs second-to-last (before wasserpumpe)
- **Reason**: Heavy Selenium scraper, run after lightweight scrapers

### Memory Considerations
- Uses Selenium (memory-intensive)
- Runs near the end to avoid memory issues
- Garbage collection after completion

## Configuration

### In config.py
```python
"pumpenheizung": {
    "base_url": "https://pumpen-heizung.de",
    "sheet_id": "YOUR_SHEET_ID_HERE"
}
```

## Troubleshooting

### Issue: Timeout Loading Page
**Solution**: Increase timeout in `init_driver()`:
```python
self.driver.set_page_load_timeout(180)  # 3 minutes
```

### Issue: No Products Found
**Cause**: Website structure changed
**Solution**: Check HTML selectors in `get_product_urls_from_homepage()`

### Issue: ChromeDriver Error
**Solution**: Update undetected-chromedriver:
```bash
pip install --upgrade undetected-chromedriver
```

## Notes

1. **Client Priority**: Client emphasized this website is "very important"
2. **Slow Website**: Be patient - website is naturally very slow
3. **Selenium Required**: Cannot use cloudscraper due to JavaScript requirements
4. **Production Ready**: Fully tested and integrated into production pipeline

## Next Steps

1. ✅ Scraper created and tested
2. ✅ Added to production pipeline
3. ✅ Configuration added to config.py
4. ⏳ Deploy to Render (manual step by user)
5. ⏳ Monitor first production run

---

**Status**: Ready for production deployment
**Last Updated**: 2026-02-15
