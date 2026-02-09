# Quick Start Guide

Get your first scraper running in 10 minutes.

## Step 1: Setup (2 minutes)

```bash
# Install dependencies
pip3 install -r requirements.txt

# Add your Google Sheets credentials
mkdir -p credentials
cp /path/to/your/credentials.json credentials/

# Test the framework
python3 test_framework.py
```

## Step 2: Create Your First Scraper (5 minutes)

```bash
# Copy the template
cp scraper_template.py my_first_scraper.py
```

Edit `my_first_scraper.py`:

```python
# Change the scraper name
SCRAPER_NAME = "my_first_scraper"

# In get_product_urls(), add your logic:
def get_product_urls(self) -> List[str]:
    # Example: scrape from sitemap
    sitemap_url = "https://your-site.com/sitemap.xml"
    response = self.make_request(sitemap_url)
    if response:
        soup = self.parse_html(response.text)
        locs = soup.find_all('loc')
        return [loc.text for loc in locs if '/product/' in loc.text]
    return []

# In scrape_product(), extract the data:
def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
    response = self.make_request(url)
    if not response:
        return None
    
    soup = self.parse_html(response.text)
    
    # Use CSS selectors to extract data
    return {
        'product_name': soup.select_one('h1.title').text.strip(),
        'sku': soup.select_one('span.sku').text.strip(),
        'category': soup.select_one('span.category').text.strip(),
        'price': soup.select_one('span.price').text.strip(),
        'availability': 'In Stock',
        'description': soup.select_one('div.description').text.strip(),
        'product_image': soup.select_one('img.product')['src'],
        'product_url': url
    }
```

## Step 3: Configure (1 minute)

Edit `config.py`:

```python
# Add your scraper config
SCRAPER_CONFIGS = {
    "my_first_scraper": {
        "base_url": "https://your-site.com",
        "sitemap_url": "https://your-site.com/sitemap.xml",
    }
}

# Add your Google Sheet ID
SHEET_IDS = {
    "my_first_scraper": "1abc123def456ghi789jkl"  # Get from Sheet URL
}
```

## Step 4: Test Locally (2 minutes)

```bash
# Test scraping (CSV output only)
python3 my_first_scraper.py

# Check the output
cat data/my_first_scraper.csv
cat logs/my_first_scraper.log

# Test with Google Sheets push
python3 my_first_scraper.py --push-to-sheets
```

## Step 5: Deploy (Optional)

```bash
# Upload to server
scp -r . root@45.32.157.30:/root/solar-scrapers/

# SSH and test
ssh root@45.32.157.30
cd /root/solar-scrapers
python3 my_first_scraper.py --push-to-sheets

# Setup nightly cron job
./setup_cron.sh
```

## Done! 🎉

Your scraper is now:
- ✅ Scraping product data
- ✅ Saving to CSV
- ✅ Pushing to Google Sheets
- ✅ Ready for Power BI connection
- ✅ Running automatically every night (if deployed)

## Next Steps

1. **Add more scrapers**: Copy the template for each website
2. **Batch execution**: Add scrapers to `run_all_scrapers.sh`
3. **Monitor**: Check logs regularly
4. **Optimize**: Adjust delays and selectors as needed

## Tips for Finding CSS Selectors

1. Open the product page in Chrome
2. Right-click on the element → Inspect
3. In DevTools, right-click the HTML element
4. Copy → Copy selector
5. Use that selector in your scraper

Example:
```python
# If Chrome gives you: #product > div > h1.title
product_name = soup.select_one('#product > div > h1.title').text.strip()

# Or use simpler selectors:
product_name = soup.select_one('h1.title').text.strip()
```

## Common Patterns

### Pattern 1: Sitemap Scraping
```python
def get_product_urls(self):
    response = self.make_request("https://site.com/sitemap.xml")
    soup = self.parse_html(response.text)
    return [loc.text for loc in soup.find_all('loc') if '/product/' in loc.text]
```

### Pattern 2: Category Page Scraping
```python
def get_product_urls(self):
    urls = []
    for page in range(1, 10):  # Paginated categories
        response = self.make_request(f"https://site.com/products?page={page}")
        soup = self.parse_html(response.text)
        links = soup.select('a.product-link')
        urls.extend([link['href'] for link in links])
    return urls
```

### Pattern 3: API Endpoint
```python
def get_product_urls(self):
    response = self.make_request("https://site.com/api/products")
    data = response.json()
    return [f"https://site.com/product/{p['id']}" for p in data['products']]
```

## Need Help?

1. Check `README.md` for detailed documentation
2. Check `DEPLOYMENT.md` for server setup
3. Run `python3 test_framework.py` to diagnose issues
4. Check logs in `logs/` directory
5. Review `sample_scraper.py` for a working example

Happy scraping! 🚀
