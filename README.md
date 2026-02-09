# Solar Equipment Price Scraping System

Production-ready web scraping framework for solar equipment price comparison.

## 🎯 Project Overview

This system scrapes solar equipment prices from 10 websites, standardizes the data, and automatically pushes it to Google Sheets for Power BI integration.

## 📁 Project Structure

```
solar-scrapers/
├── config.py                  # Central configuration
├── base_scraper.py           # Base scraper class (inherit from this)
├── google_sheets_helper.py   # Google Sheets integration
├── scraper_template.py       # Template for new scrapers
├── sample_scraper.py         # Working example scraper
├── run_all_scrapers.sh       # Batch execution script
├── setup_cron.sh             # Cron job setup
├── requirements.txt          # Python dependencies
├── credentials/              # Google Sheets credentials
│   └── credentials.json
├── data/                     # CSV output files
│   └── *.csv
└── logs/                     # Log files
    └── *.log
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip3 install -r requirements.txt

# Create credentials directory
mkdir -p credentials

# Add your credentials.json file
cp /path/to/your/credentials.json credentials/
```

### 2. Create Your First Scraper

```bash
# Copy the template
cp scraper_template.py my_scraper.py

# Edit the file and customize:
# - SCRAPER_NAME
# - get_product_urls() method
# - scrape_product() method
```

### 3. Configure

Edit `config.py`:

```python
# Add your scraper configuration
SCRAPER_CONFIGS = {
    "my_scraper": {
        "base_url": "https://example.com",
        "sitemap_url": "https://example.com/sitemap.xml",
    }
}

# Add Google Sheet ID
SHEET_IDS = {
    "my_scraper": "your_google_sheet_id_here"
}
```

### 4. Test Locally

```bash
# Run without Google Sheets (CSV only)
python3 my_scraper.py

# Run with Google Sheets push
python3 my_scraper.py --push-to-sheets

# Check output
cat data/my_scraper.csv
cat logs/my_scraper.log
```

### 5. Deploy to Production

```bash
# Upload to your server
scp -r . root@45.32.157.30:/root/solar-scrapers/

# SSH into server
ssh root@45.32.157.30

# Setup cron job for nightly runs
cd /root/solar-scrapers
chmod +x setup_cron.sh
./setup_cron.sh
```

## 📝 Creating a New Scraper

### Step-by-Step Guide

1. **Copy the template:**
   ```bash
   cp scraper_template.py priwatt_scraper.py
   ```

2. **Update SCRAPER_NAME:**
   ```python
   SCRAPER_NAME = "priwatt"
   ```

3. **Implement get_product_urls():**
   ```python
   def get_product_urls(self) -> List[str]:
       # Option A: Parse sitemap
       sitemap_url = "https://priwatt.de/sitemap.xml"
       response = self.make_request(sitemap_url)
       # ... extract URLs
       
       # Option B: Scrape category pages
       # ... your logic
       
       return product_urls
   ```

4. **Implement scrape_product():**
   ```python
   def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
       response = self.make_request(url)
       soup = self.parse_html(response.text)
       
       # Extract data using CSS selectors
       product_name = soup.select_one('h1.title').text.strip()
       price = soup.select_one('span.price').text.strip()
       # ... etc
       
       return {
           'product_name': product_name,
           'sku': sku,
           'category': category,
           'price': price,
           'availability': availability,
           'description': description,
           'product_image': image_url,
           'product_url': url
       }
   ```

5. **Add to config.py:**
   ```python
   SCRAPER_CONFIGS["priwatt"] = {
       "base_url": "https://priwatt.de",
       "sitemap_url": "https://priwatt.de/sitemap.xml",
   }
   
   SHEET_IDS["priwatt"] = "your_sheet_id"
   ```

6. **Add to run_all_scrapers.sh:**
   ```bash
   run_scraper "priwatt_scraper.py"
   ```

## 🔧 Framework Features

### Base Scraper Class

The `BaseScraper` class provides:

- ✅ **Automatic retry logic** - Retries failed requests up to 3 times
- ✅ **Rate limiting** - Random delays between requests (1-3 seconds)
- ✅ **User agent rotation** - Avoids detection
- ✅ **Error handling** - Comprehensive logging
- ✅ **CSV output** - Standardized format
- ✅ **Logging** - Rotating file logs with console output

### Google Sheets Integration

```python
from google_sheets_helper import GoogleSheetsHelper

helper = GoogleSheetsHelper()
helper.push_csv_to_sheet("sheet_id", "data/output.csv")
```

Features:
- Automatic authentication
- Clear and update sheets
- Create new sheets
- Error handling

## 📊 Data Structure

All scrapers output CSV with these columns:

```
product_name, sku, category, price, availability, description, product_image, product_url
```

This matches your existing system and Power BI requirements.

## 🤖 Automation

### Cron Job Setup

```bash
# Run setup script
./setup_cron.sh

# Verify
crontab -l

# Manual cron entry (runs at 2 AM daily):
0 2 * * * cd /root/solar-scrapers && ./run_all_scrapers.sh --push-to-sheets
```

### Batch Execution

```bash
# Run all scrapers
./run_all_scrapers.sh

# Run all scrapers and push to Google Sheets
./run_all_scrapers.sh --push-to-sheets
```

## 📈 Monitoring

### Check Logs

```bash
# Individual scraper logs
tail -f logs/priwatt.log

# Master batch log
tail -f logs/master_*.log

# Cron execution log
tail -f logs/cron.log
```

### Log Rotation

Logs automatically rotate when they reach 10MB. Up to 5 backup files are kept.

## 🛠️ Troubleshooting

### Common Issues

**1. Import errors:**
```bash
pip3 install -r requirements.txt
```

**2. Google Sheets authentication fails:**
- Check credentials.json is in credentials/ folder
- Verify service account email has access to sheets
- Check sheet IDs in config.py

**3. No products found:**
- Check website structure hasn't changed
- Verify selectors in scrape_product()
- Check logs for specific errors

**4. Rate limiting / blocked:**
- Increase delays in config.py (MIN_DELAY, MAX_DELAY)
- Add more user agents
- Check robots.txt

### Debug Mode

Enable detailed logging:

```python
# In config.py
LOG_LEVEL = "DEBUG"
```

## 📋 Checklist for Each Scraper

- [ ] Copy scraper_template.py
- [ ] Update SCRAPER_NAME
- [ ] Implement get_product_urls()
- [ ] Implement scrape_product()
- [ ] Add config to config.py
- [ ] Add Google Sheet ID
- [ ] Test locally (CSV output)
- [ ] Test Google Sheets push
- [ ] Add to run_all_scrapers.sh
- [ ] Deploy to server
- [ ] Verify cron execution

## 🔐 Security Notes

- Never commit credentials.json to git
- Use environment variables for sensitive data in production
- Respect robots.txt and website terms of service
- Implement appropriate rate limiting

## 📞 Support

For issues or questions:
1. Check logs in logs/ directory
2. Review scraper-specific log file
3. Check master batch log
4. Verify configuration in config.py

## 🎓 Best Practices

1. **Test locally first** - Always test before deploying
2. **Start simple** - Get basic scraping working, then add features
3. **Handle errors gracefully** - Use try/except blocks
4. **Log everything** - Helps with debugging
5. **Be respectful** - Use appropriate delays
6. **Keep it DRY** - Reuse base class methods
7. **Document selectors** - Comment your CSS selectors

## 🛒 Shopify Integration

The system now includes **modern Shopify integration** to automatically sync scraped products to your Shopify store.

### Quick Start

```bash
# Test connection
python shopify_integration.py

# Sync products from CSV
python shopify_integration.py data/heima24.csv 10
```

### Documentation

- **📖 Start here:** `SHOPIFY_INTEGRATION_UPDATED.md` - Overview of new features
- **🚀 Quick reference:** `SHOPIFY_QUICK_REFERENCE.md` - Common tasks
- **⚙️ Modern setup:** `SHOPIFY_MODERN_SETUP.md` - OAuth 2.0 setup (recommended)
- **📊 Comparison:** `SHOPIFY_COMPARISON.md` - Legacy vs Modern methods
- **🔑 Legacy setup:** `GET_SHOPIFY_TOKEN.md` - Traditional API token setup

### Two Integration Methods

**Legacy Integration** (`shopify_integration.py`)
- ✅ Works now with your current credentials
- ✅ Simple setup
- ⚠️ Older authentication method

**Modern OAuth Integration** (`shopify_oauth_integration.py`)
- ✅ Recommended by Shopify
- ✅ 6x faster product searches (GraphQL)
- ✅ Better security (token-based)
- ⚠️ Requires 15-minute setup

### Test Both Methods

```bash
# Compare both integrations
python test_shopify_both.py

# Test with specific SKU
python test_shopify_both.py ABC123
```

### Features

- ✅ Create/update products automatically
- ✅ Match by SKU, EAN, or title
- ✅ Apply price markup (percentage or fixed)
- ✅ Sync product images and metadata
- ✅ Batch import from CSV files
- ✅ Rate limiting handled automatically

See `SHOPIFY_INTEGRATION_UPDATED.md` for complete details.

## 📦 Next Steps

1. Build your 10 scrapers using the template
2. Test each one individually
3. Add all to run_all_scrapers.sh
4. Deploy to server
5. Setup cron job
6. Monitor for first few days
7. Connect Google Sheets to Power BI
8. **Optional:** Set up Shopify integration for e-commerce

Good luck! 🚀
