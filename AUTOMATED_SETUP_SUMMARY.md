# Automated Nightly Scraping - Setup Summary

## What You're Getting

A fully automated web scraping system that runs every night at midnight (00:00) and updates your Google Sheets with fresh product data from 9 websites.

## The 9 Websites Being Scraped

1. **meinhausshop.de** - ~169,000 products
2. **heima24.de** - ~24,500 products
3. **sanundo.de** - ~21,200 products
4. **heizungsdiscount24.de** - ~68,300 products
5. **wolfonlineshop.de** - ~160 products
6. **st-shop24.de** - ~243 products
7. **selfio.de** - Shopware 6 platform
8. **pumpe24.de** - ~46 products (Cloudflare protected)
9. **wasserpumpe.de** - ~49 products (Cloudflare protected)

**Total: ~283,000+ products scraped nightly**

## How It Works

### Every Night at Midnight (00:00):
1. All 9 scrapers start simultaneously (parallel execution)
2. Each scraper visits its website and extracts product data
3. Data is saved to CSV files locally
4. Data is automatically pushed to your Google Sheets
5. Logs are saved for monitoring
6. Process repeats the next night

### No Manual Work Required
- Runs automatically via cron job
- Continues even if you're logged out
- Updates Google Sheets automatically
- Handles errors gracefully
- Logs everything for monitoring

## Quick Setup (3 Steps)

### Linux/Mac:

### 1. Upload Files to Your Server
```bash
scp -r * user@server:/path/to/scrapers/
```

### 2. Install Dependencies
```bash
cd /path/to/scrapers
pip3 install -r requirements.txt
```

### 3. Setup Cron Job
```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

### Windows:

### 1. Install Dependencies
```powershell
cd C:\path\to\scrapers
pip install -r requirements.txt
```

### 2. Setup Task Scheduler
```powershell
.\setup_windows_task.ps1
```

**Done!** The system will now run automatically every night at midnight.

## Your Google Sheets

All data is pushed to these sheets automatically:

| Website | Sheet ID | URL |
|---------|----------|-----|
| meinhausshop | 1KaMWOGh9KEPvvxWQRKLu-fLr0-aSLdhn5IbdZ0XyvTQ | [Open Sheet](https://docs.google.com/spreadsheets/d/1KaMWOGh9KEPvvxWQRKLu-fLr0-aSLdhn5IbdZ0XyvTQ) |
| heima24 | 1nfHVN4RZM-tED-HtXUWV7bwtAWjctih7dJ2eOyTRj08 | [Open Sheet](https://docs.google.com/spreadsheets/d/1nfHVN4RZM-tED-HtXUWV7bwtAWjctih7dJ2eOyTRj08) |
| sanundo | 1ygsm7nK3glzapTCoM0X7Hk3x1-xY3ieTqRCdXJN5Y8A | [Open Sheet](https://docs.google.com/spreadsheets/d/1ygsm7nK3glzapTCoM0X7Hk3x1-xY3ieTqRCdXJN5Y8A) |
| heizungsdiscount24 | 1dwls46f4xW7Td5XrV8ShvLdwsPJwQhPieH342BOEZ8o | [Open Sheet](https://docs.google.com/spreadsheets/d/1dwls46f4xW7Td5XrV8ShvLdwsPJwQhPieH342BOEZ8o) |
| wolfonlineshop | 1IR3BAObUJf4cUxdX9OF1zka0YsOrP35c-n8F4xIl3a8 | [Open Sheet](https://docs.google.com/spreadsheets/d/1IR3BAObUJf4cUxdX9OF1zka0YsOrP35c-n8F4xIl3a8) |
| st_shop24 | 1inV05kOmYe53iq0ujyDafftzxZgqWVnBriRbD-BOd_k | [Open Sheet](https://docs.google.com/spreadsheets/d/1inV05kOmYe53iq0ujyDafftzxZgqWVnBriRbD-BOd_k) |
| selfio | 19evdUWIJX9hLK46XYp5avvlW9KZhGayjnw6fkwn2CfE | [Open Sheet](https://docs.google.com/spreadsheets/d/19evdUWIJX9hLK46XYp5avvlW9KZhGayjnw6fkwn2CfE) |
| pumpe24 | 1eKkepxz9FtDVQNaQmBmPfnTqTcFz7kai0dxJ0JCwuGU | [Open Sheet](https://docs.google.com/spreadsheets/d/1eKkepxz9FtDVQNaQmBmPfnTqTcFz7kai0dxJ0JCwuGU) |
| wasserpumpe | 1iGmt66Y4mKwC06aT0NhKzWZ8GfcCtgY0oPdYVSY4Jz4 | [Open Sheet](https://docs.google.com/spreadsheets/d/1iGmt66Y4mKwC06aT0NhKzWZ8GfcCtgY0oPdYVSY4Jz4) |

**Important:** Make sure the service account `webscraping-solarics@webscrapingmajd2.iam.gserviceaccount.com` has Editor access to all sheets.

## Data Format

Each sheet contains these columns:
- **manufacturer** - Product manufacturer
- **category** - Product category
- **name** - Product name
- **title** - Product title
- **article_number** - SKU/Article number
- **price_net** - Net price (excluding VAT)
- **price_gross** - Gross price (including 19% VAT)
- **ean** - EAN barcode
- **product_image** - Image URL
- **product_url** - Product page URL

## Monitoring

### Check if it's running:
```bash
# View cron jobs
crontab -l

# Check today's log
tail -f cron_logs/cron_$(date +%Y%m%d).log

# Check individual scraper
tail -f logs/meinhausshop.log
```

### Check for errors:
```bash
grep ERROR logs/*.log
```

### Verify Google Sheets are updating:
Just open any sheet and check the last modified date.

## Change the Schedule

Edit `setup_cron.sh` and change this line:
```bash
CRON_ENTRY="0 2 * * * ..."
```

Common schedules:
- `0 0 * * *` - Every night at midnight (default)
- `0 2 * * *` - Every night at 2 AM
- `0 3 * * *` - Every night at 3 AM
- `0 0,12 * * *` - Twice daily at midnight and noon
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 1` - Every Monday at midnight

Then run `./setup_cron.sh` again.

## Manual Run

To run the scrapers manually anytime:
```bash
./run_all_scrapers.sh
```

Or run a single scraper:
```bash
python3 meinhausshop_scraper.py
```

## Files & Folders

```
scrapers/
├── run_all_scrapers_parallel.py  # Main script (runs all scrapers)
├── run_all_scrapers.sh           # Bash wrapper for cron
├── setup_cron.sh                 # Cron installation script
├── config.py                     # All settings and Sheet IDs
├── *_scraper.py                  # Individual scraper files
├── data/                         # CSV output files
├── logs/                         # Individual scraper logs
├── cron_logs/                    # Cron execution logs
└── credentials/                  # Google service account credentials
```

## Documentation

- **CRON_SETUP.md** - Detailed cron documentation
- **DEPLOYMENT.md** - Complete deployment guide
- **TECHNICAL_REPORT.md** - Full technical documentation
- **QUICKSTART.md** - Quick start guide

## Support

If something goes wrong:
1. Check `cron_logs/` for execution logs
2. Check `logs/` for individual scraper logs
3. Verify Google Sheets access
4. Test manually: `./run_all_scrapers.sh`

## What's Next (Future Enhancements)

As mentioned in the technical report, the next phase could include:
- **Shopify Integration** - Direct API integration to import/update products in your Shopify store
- **Price Monitoring** - Track price changes over time
- **Email Alerts** - Get notified of scraping failures or price changes
- **Dashboard** - Web interface to monitor scraping status

## Summary

✓ 9 websites scraped automatically every night at midnight
✓ ~283,000+ products updated in Google Sheets
✓ No manual work required
✓ Runs even when you're logged out
✓ Logs everything for monitoring
✓ Easy to modify schedule or add new sites

**Setup time: 5 minutes**
**Maintenance: Check logs weekly**
