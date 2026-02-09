# 🚀 START HERE - Your First Steps

Welcome! This guide will get you from zero to your first working scraper in 15 minutes.

## ⚡ Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Add Your Credentials

```bash
# Create credentials directory (already exists)
# Copy your credentials.json file
cp /path/to/your/credentials.json credentials/

# Verify it's there
ls -l credentials/credentials.json
```

### 3. Test the Framework

```bash
python3 test_framework.py
```

You should see all tests pass (some warnings about credentials are OK if you haven't added them yet).

## 🎯 Your First Scraper (10 minutes)

### Step 1: Choose a Website

Pick one of your 10 solar equipment websites. For this example, let's say it's "priwatt.de"

### Step 2: Create the Scraper

```bash
# Copy the template
cp scraper_template.py priwatt_scraper.py
```

### Step 3: Edit the Scraper

Open `priwatt_scraper.py` and make these changes:

```python
# Line 18: Change the scraper name
SCRAPER_NAME = "priwatt"  # Change from "sample_scraper"

# Line 30: Add your base URL
self.base_url = "https://priwatt.de"
```

### Step 4: Implement get_product_urls()

Find the `get_product_urls()` method (around line 50) and add your logic:

```python
def get_product_urls(self) -> List[str]:
    """Get product URLs from sitemap."""
    product_urls = []
    
    # Try sitemap first
    sitemap_url = "https://priwatt.de/sitemap_products.xml"
    response = self.make_request(sitemap_url)
    
    if response:
        soup = self.parse_html(response.text)
        locs = soup.find_all('loc')
        for loc in locs:
            url = loc.text.strip()
            # Filter for product pages
            if '/products/' in url:
                product_urls.append(url)
    
    return product_urls
```

### Step 5: Implement scrape_product()

Find the `scrape_product()` method (around line 80) and customize the CSS selectors:

**How to find selectors:**
1. Open a product page in Chrome
2. Right-click on the product name → Inspect
3. In DevTools, right-click the HTML element → Copy → Copy selector
4. Use that selector in your code

```python
def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
    """Scrape individual product page."""
    response = self.make_request(url)
    if not response:
        return None
    
    try:
        soup = self.parse_html(response.text)
        
        # TODO: Replace these selectors with actual ones from the website
        product_name = soup.select_one('h1.product-title')
        product_name = product_name.text.strip() if product_name else ""
        
        sku = soup.select_one('span.sku')
        sku = sku.text.strip() if sku else ""
        
        # ... continue for all fields
        
        return {
            'product_name': product_name,
            'sku': sku,
            'category': category,
            'price': price,
            'availability': availability,
            'description': description,
            'product_image': product_image,
            'product_url': url
        }
    except Exception as e:
        self.logger.error(f"Error parsing {url}: {e}")
        return None
```

### Step 6: Configure

Edit `config.py` and add your scraper:

```python
# Around line 50: Add scraper config
SCRAPER_CONFIGS = {
    "priwatt": {
        "base_url": "https://priwatt.de",
        "sitemap_url": "https://priwatt.de/sitemap_products.xml",
        "requires_login": False,
    },
    # ... other scrapers
}

# Around line 20: Add Google Sheet ID
SHEET_IDS = {
    "priwatt": "1abc123def456ghi789jkl",  # Get from your Sheet URL
    # ... other scrapers
}
```

### Step 7: Test It!

```bash
# Test scraping (CSV only)
python3 priwatt_scraper.py

# Check the output
cat data/priwatt.csv
cat logs/priwatt.log

# If it works, test Google Sheets push
python3 priwatt_scraper.py --push-to-sheets
```

## ✅ Success Checklist

After running your scraper, verify:

- [ ] CSV file created in `data/priwatt.csv`
- [ ] Log file created in `logs/priwatt.log`
- [ ] CSV has all 8 columns
- [ ] Products are being scraped (check CSV content)
- [ ] No errors in log file
- [ ] Google Sheets updated (if you used --push-to-sheets)

## 🎉 You Did It!

Congratulations! You now have:
- ✅ A working scraper
- ✅ CSV output
- ✅ Google Sheets integration
- ✅ Comprehensive logging

## 📚 Next Steps

### Build Your Remaining 9 Scrapers

For each website:
1. Copy the template: `cp scraper_template.py website_scraper.py`
2. Update SCRAPER_NAME
3. Implement get_product_urls()
4. Implement scrape_product()
5. Add to config.py
6. Test locally
7. Add to run_all_scrapers.sh

**Use the checklist:** See `SCRAPER_CHECKLIST.md` for detailed steps.

### Deploy to Server

Once all scrapers are working locally:

```bash
# Upload to server
scp -r . root@45.32.157.30:/root/solar-scrapers/

# SSH and setup
ssh root@45.32.157.30
cd /root/solar-scrapers
pip3 install -r requirements.txt
./setup_cron.sh
```

**Full deployment guide:** See `DEPLOYMENT.md`

## 📖 Documentation Quick Links

- **QUICKSTART.md** - 10-minute getting started guide
- **README.md** - Complete framework documentation
- **SCRAPER_CHECKLIST.md** - Checklist for each scraper
- **DEPLOYMENT.md** - Server deployment guide
- **ARCHITECTURE.md** - System architecture overview
- **PROJECT_SUMMARY.md** - Project overview

## 💡 Pro Tips

### Finding CSS Selectors

```
1. Open product page in Chrome
2. Right-click element → Inspect
3. In DevTools, right-click HTML → Copy → Copy selector
4. Paste into your code
5. Test and simplify if needed
```

### Testing Individual Methods

```python
# Test get_product_urls() alone
python3 -c "
from priwatt_scraper import PriwattScraper
scraper = PriwattScraper()
urls = scraper.get_product_urls()
print(f'Found {len(urls)} URLs')
print(urls[:5])
"

# Test scrape_product() on one URL
python3 -c "
from priwatt_scraper import PriwattScraper
scraper = PriwattScraper()
data = scraper.scrape_product('https://priwatt.de/product/example')
print(data)
"
```

### Common Issues

**No products found:**
- Check sitemap URL is correct
- Verify CSS selectors in browser DevTools
- Check logs for errors

**Missing data fields:**
- Verify selectors are correct
- Check if data is in different location
- Add fallback selectors

**Getting blocked:**
- Increase delays in config.py
- Check robots.txt
- Reduce request frequency

## 🆘 Need Help?

1. **Run tests:** `python3 test_framework.py`
2. **Check logs:** `cat logs/your_scraper.log`
3. **Review example:** Look at `sample_scraper.py`
4. **Read docs:** Check README.md for detailed info

## 🎯 Your Goal

Build 10 scrapers following this pattern:

```
✅ Scraper 1 (priwatt)      - Done!
⬜ Scraper 2                - Next
⬜ Scraper 3
⬜ Scraper 4
⬜ Scraper 5
⬜ Scraper 6
⬜ Scraper 7
⬜ Scraper 8
⬜ Scraper 9
⬜ Scraper 10
```

**Estimated time:** 1.5-2 hours per scraper = 15-20 hours total

## 🚀 Ready to Build?

You have everything you need:
- ✅ Framework is ready
- ✅ Template is ready
- ✅ Documentation is ready
- ✅ Example is ready

Just follow the pattern for each website!

Good luck! 🎉

---

**Quick Commands Reference:**

```bash
# Test framework
python3 test_framework.py

# Create new scraper
cp scraper_template.py new_scraper.py

# Test scraper
python3 new_scraper.py

# Test with Google Sheets
python3 new_scraper.py --push-to-sheets

# Run all scrapers
./run_all_scrapers.sh --push-to-sheets

# Deploy to server
scp -r . root@45.32.157.30:/root/solar-scrapers/

# Setup cron
./setup_cron.sh
```
