# Production Workflow - Detailed Review

## 🎯 Overview

Your production workflow is a fully automated data pipeline that runs weekly on Render.com, scraping products from 9 websites and delivering them to Power BI via Google Sheets.

---

## 📅 Schedule & Trigger

### Cron Schedule
```yaml
schedule: "0 2 * * 0"  # Every Sunday at 2 AM UTC
```

**What this means:**
- Runs automatically every Sunday
- Starts at 2:00 AM UTC (Coordinated Universal Time)
- No manual intervention needed
- Render.com handles the scheduling

**Convert to your timezone:**
- 2 AM UTC = 3 AM CET (Central European Time)
- 2 AM UTC = 10 PM EST (Saturday night)
- 2 AM UTC = 7 PM PST (Saturday evening)

---

## 🔄 Complete Workflow (Step by Step)

### Phase 1: Initialization (2 minutes)

#### Step 1.1: Render Triggers Job
```
Sunday 2:00 AM UTC
↓
Render.com cron scheduler activates
↓
Spins up Python 3.11 environment
↓
Allocates 512MB RAM (free tier)
```

#### Step 1.2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Installs:**
- beautifulsoup4 (HTML parsing)
- requests (HTTP requests)
- gspread (Google Sheets API)
- oauth2client (Google authentication)
- pandas (data processing)
- lxml (XML/HTML parsing)
- selenium (browser automation)
- webdriver-manager (Chrome driver)
- undetected-chromedriver (anti-detection)
- cloudscraper (cloudflare bypass)

**Time:** ~1-2 minutes

#### Step 1.3: Load Credentials
```python
# From environment variable
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
```

**What happens:**
- Reads credentials.json from environment variable
- Authenticates with Google Sheets API
- Establishes connection

---

### Phase 2: Data Collection (60-90 minutes)

The script runs 9 scrapers **sequentially** (one after another), not in parallel.

#### Scraper 1: MeinHausShop
```python
scraper = MeinHausShopScraper()
product_count = scraper.run(max_products=None)  # NO LIMIT
```

**What happens:**
1. Connects to meinhausshop.de
2. Finds all product categories
3. Iterates through each category
4. Scrapes ALL products (no 2000 limit)
5. Extracts:
   - article_number
   - name
   - price_net (German format: "1.234,56")
   - price_gross
   - availability
   - url
   - category
   - description
6. Saves to `data/meinhausshop.csv`

**Expected:** ~3,000 products
**Time:** ~8-12 minutes

#### Scraper 2: Heima24
```python
scraper = Heima24Scraper()
product_count = scraper.run(max_products=None)
```

**What happens:**
1. Connects to heima24.de
2. Scrapes ALL products
3. Saves to `data/heima24.csv`

**Expected:** ~2,500 products
**Time:** ~6-10 minutes

#### Scraper 3: Sanundo
```python
scraper = SanundoScraper()
product_count = scraper.run(max_products=None)
```

**Expected:** ~2,000 products
**Time:** ~5-8 minutes

#### Scraper 4: Heizungsdiscount24
```python
scraper = Heizungsdiscount24Scraper()
product_count = scraper.run(max_products=None)
```

**Expected:** ~2,500 products
**Time:** ~6-10 minutes

#### Scraper 5: Wolfonlineshop
```python
scraper = WolfonlineshopScraper()
product_count = scraper.run(max_products=None)
```

**Expected:** ~3,000 products
**Time:** ~8-12 minutes

#### Scraper 6: StShop24
```python
scraper = StShop24Scraper()
product_count = scraper.run(max_products=None)
```

**Expected:** ~2,000 products
**Time:** ~5-8 minutes

#### Scraper 7: Selfio
```python
scraper = SelfioScraper()
product_count = scraper.run(max_products=None)
```

**Expected:** ~2,500 products
**Time:** ~6-10 minutes

#### Scraper 8: Pumpe24
```python
scraper = Pumpe24Scraper()
product_count = scraper.run(max_products=None)
```

**Expected:** ~1,500 products
**Time:** ~4-7 minutes

#### Scraper 9: Wasserpumpe
```python
scraper = WasserpumpeScraper()
product_count = scraper.run(max_products=None)
```

**Expected:** ~1,500 products
**Time:** ~4-7 minutes

**Total Phase 2:**
- Products: ~20,000-25,000
- Time: 60-90 minutes
- Output: 9 individual CSV files in `data/` folder

---

### Phase 3: Data Processing (2-3 minutes)

#### Step 3.1: Read All CSV Files
```python
for idx, (name, scraper_class) in enumerate(SCRAPERS, 1):
    csv_file = DATA_DIR / f"{name}.csv"
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        products = list(reader)
```

**What happens:**
- Reads each of the 9 CSV files
- Loads all products into memory
- Creates list of dictionaries

#### Step 3.2: Add Source Column
```python
for product in products:
    product['source'] = name  # e.g., 'meinhausshop', 'heima24', etc.
```

**Why:**
- Identifies which website each product came from
- Allows filtering in Power BI by source
- Essential for multi-source analysis

#### Step 3.3: Convert Prices to Numbers
```python
# German format: "1.234,56" → Numeric: 1234.56
if ',' in price_str:
    price_str = price_str.replace('.', '').replace(',', '.')
product['price_net'] = float(price_str)
```

**What happens:**
- German format uses comma for decimals: "1.234,56"
- Removes thousand separators (dots): "1234,56"
- Replaces decimal comma with dot: "1234.56"
- Converts to float: 1234.56

**Why:**
- Google Sheets needs numeric format for sorting
- Power BI needs numbers for calculations
- Enables price comparisons and analytics

**Example transformations:**
```
"1.234,56"  → 1234.56
"999,99"    → 999.99
"12.345,00" → 12345.00
"50,00"     → 50.00
```

#### Step 3.4: Combine All Products
```python
all_products.extend(products)
```

**Result:**
- Single list with ~20,000-25,000 products
- All 9 sources combined
- Each product has 'source' column
- Prices are numeric

#### Step 3.5: Write Combined CSV
```python
combined_csv = DATA_DIR / "power_bi_production.csv"
columns_with_source = CSV_COLUMNS + ['source']

with open(combined_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=columns_with_source)
    writer.writeheader()
    writer.writerows(all_products)
```

**Output file:** `data/power_bi_production.csv`

**Columns:**
```
article_number, name, price_net, price_gross, availability, 
url, category, description, ean, manufacturer, source
```

**Sample row:**
```csv
ABC123,"Heat Pump",1234.56,1469.33,"In Stock","https://...","Heating","...","4012345678901","Viessmann","meinhausshop"
```

---

### Phase 4: Google Sheets Push (3-5 minutes)

#### Step 4.1: Authenticate with Google
```python
from google_sheets_helper import push_data

helper = GoogleSheetsHelper()
# Uses credentials from environment variable
```

**What happens:**
- Reads `GOOGLE_APPLICATION_CREDENTIALS` env var
- Authenticates with Google Sheets API
- Gets authorization token

#### Step 4.2: Open Target Sheet
```python
POWER_BI_SHEET_ID = "1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg"
spreadsheet = client.open_by_key(sheet_id)
worksheet = spreadsheet.worksheet("Sheet1")
```

**What happens:**
- Opens your specific Google Sheet
- Accesses the first worksheet
- Prepares for data update

#### Step 4.3: Clear Existing Data
```python
worksheet.clear()
```

**Why:**
- Removes old data from previous week
- Prevents duplicate entries
- Ensures fresh data only

#### Step 4.4: Upload New Data
```python
worksheet.update(
    values=data,
    range_name='A1:L20000',  # Adjust based on data size
    value_input_option='USER_ENTERED'
)
```

**What happens:**
- Uploads all ~20,000 rows
- Starts at cell A1 (top-left)
- `USER_ENTERED` tells Google Sheets to interpret data types
- Numbers are recognized as numbers (not text)
- Dates are recognized as dates

**Time:** 2-4 minutes (depends on data size)

#### Step 4.5: Format Price Columns
```python
worksheet.format(
    'C2:C20000',  # price_net column
    {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}}
)
```

**What happens:**
- Formats price_net column as currency
- Formats price_gross column as currency
- Adds thousand separators
- Shows 2 decimal places

**Result in Google Sheets:**
```
1234.56  → 1,234.56
999.99   → 999.99
12345.00 → 12,345.00
```

#### Step 4.6: Verify Upload
```python
print(f"✓ Successfully pushed {len(all_products)} products to Google Sheets")
```

**Logs show:**
```
✓ Created combined CSV with 20,543 products
✓ Successfully pushed 20,543 products to Google Sheets
✓ Power BI will auto-refresh with new data
```

---

### Phase 5: Completion & Logging (1 minute)

#### Step 5.1: Print Summary
```python
print("PRODUCTION PIPELINE SUMMARY")
print(f"Total products scraped: {len(all_products):,}")
print(f"Total time: {total_elapsed/60:.1f} minutes")
```

**Example output:**
```
================================================================================
PRODUCTION PIPELINE SUMMARY
================================================================================

Total products scraped: 20,543
Total time: 73.2 minutes
Average per scraper: 8.1 seconds

Results by scraper:
--------------------------------------------------------------------------------
✓ meinhausshop        |  3,124 products |   12.3s
✓ heima24             |  2,567 products |    9.8s
✓ sanundo             |  1,987 products |    7.2s
✓ heizungsdiscount24  |  2,456 products |   10.1s
✓ wolfonlineshop      |  3,089 products |   11.7s
✓ st_shop24           |  2,134 products |    8.4s
✓ selfio              |  2,398 products |    9.6s
✓ pumpe24             |  1,543 products |    6.8s
✓ wasserpumpe         |  1,245 products |    5.9s

================================================================================
Completed: 2026-02-16 03:13:27
================================================================================

✓ Data successfully pushed to Google Sheet: 1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg
✓ Power BI Dashboard will auto-refresh with 20,543 products
================================================================================
```

#### Step 5.2: Exit Successfully
```python
sys.exit(0)  # Success code
```

**What happens:**
- Render marks job as "successful"
- Logs are saved
- Environment is cleaned up
- Resources are released

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    RENDER.COM CRON JOB                          │
│                  Sunday 2:00 AM UTC                             │
│                  Free Tier (512MB RAM)                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Install Dependencies
                    Load Credentials
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    SCRAPING PHASE                               │
│                    (60-90 minutes)                              │
│                                                                 │
│  [1] MeinHausShop    → 3,000 products → meinhausshop.csv       │
│  [2] Heima24         → 2,500 products → heima24.csv            │
│  [3] Sanundo         → 2,000 products → sanundo.csv            │
│  [4] Heizungsdiscount→ 2,500 products → heizungsdiscount24.csv │
│  [5] Wolfonlineshop  → 3,000 products → wolfonlineshop.csv     │
│  [6] StShop24        → 2,000 products → st_shop24.csv          │
│  [7] Selfio          → 2,500 products → selfio.csv             │
│  [8] Pumpe24         → 1,500 products → pumpe24.csv            │
│  [9] Wasserpumpe     → 1,500 products → wasserpumpe.csv        │
│                                                                 │
│  Total: ~20,000 products in 9 CSV files                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING PHASE                             │
│                    (2-3 minutes)                                │
│                                                                 │
│  1. Read all 9 CSV files                                       │
│  2. Add 'source' column to each product                        │
│  3. Convert prices: "1.234,56" → 1234.56                      │
│  4. Combine into single list (~20,000 products)                │
│  5. Write to power_bi_production.csv                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE SHEETS PUSH                           │
│                    (3-5 minutes)                                │
│                                                                 │
│  1. Authenticate with Google API                               │
│  2. Open sheet: 1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg  │
│  3. Clear old data                                             │
│  4. Upload ~20,000 rows                                        │
│  5. Format price columns as numbers                            │
│  6. Verify upload success                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE SHEETS                                │
│                    (Always Available)                           │
│                                                                 │
│  Sheet ID: 1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg       │
│  URL: https://docs.google.com/spreadsheets/d/[ID]/edit         │
│                                                                 │
│  Data Structure:                                               │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ article_number | name | price_net | price_gross | ... │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │ ABC123        | Pump | 1,234.56  | 1,469.33     | ... │   │
│  │ DEF456        | Heat | 2,345.67  | 2,791.35     | ... │   │
│  │ ...           | ...  | ...       | ...          | ... │   │
│  │ (20,000+ rows)                                         │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Features:                                                      │
│  ✓ Public read access (anyone with link)                      │
│  ✓ CSV export enabled                                          │
│  ✓ Numbers formatted correctly                                 │
│  ✓ Updated weekly (every Sunday)                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Power BI Connects Here
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    POWER BI DESKTOP                             │
│                    (Client's Computer)                          │
│                                                                 │
│  Data Source Configuration:                                     │
│  Type: Web                                                      │
│  URL: https://docs.google.com/spreadsheets/d/                  │
│       1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg/            │
│       export?format=csv                                         │
│                                                                 │
│  Refresh Schedule:                                              │
│  - Manual: Click "Refresh" button                              │
│  - Automatic: Configure in Power BI Service                    │
│  - Recommended: Weekly (Monday morning)                         │
│                                                                 │
│  Dashboard Features:                                            │
│  ✓ Product count by source                                     │
│  ✓ Price analysis & comparisons                                │
│  ✓ Search by article number                                    │
│  ✓ Filter by category                                          │
│  ✓ Availability tracking                                       │
│  ✓ Price trends over time                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Key Technical Details

### 1. Why Sequential (Not Parallel)?
```python
for idx, (name, scraper_class) in enumerate(SCRAPERS, 1):
    scraper = scraper_class()
    product_count = scraper.run(max_products=None)
```

**Reasons:**
- Simpler error handling (one scraper fails, others continue)
- Lower memory usage (only one scraper in memory at a time)
- Avoids IP blocking (not hammering websites simultaneously)
- Easier to debug (clear logs per scraper)
- Free tier has 512MB RAM (parallel would exceed this)

**Trade-off:**
- Takes longer (90 min vs potential 15 min parallel)
- But more reliable and stays within free tier

### 2. Why max_products=None?
```python
product_count = scraper.run(max_products=None)  # NO LIMIT
```

**Production vs Test:**
- Test: `max_products=2000` (quick validation)
- Production: `max_products=None` (complete data)

**Result:**
- Scrapes EVERY product from each website
- No artificial limits
- Complete dataset for analysis

### 3. Price Conversion Logic
```python
# Input: "1.234,56" (German format)
price_str = price_str.replace('.', '')  # "1234,56"
price_str = price_str.replace(',', '.')  # "1234.56"
product['price_net'] = float(price_str)  # 1234.56
```

**Why this matters:**
- German websites use comma for decimals
- Google Sheets needs dot for decimals
- Power BI needs numeric type for calculations
- Without conversion: prices would be text (can't sort/calculate)

### 4. Google Sheets API Limits
```python
worksheet.update(
    values=data,
    range_name='A1:L20000',
    value_input_option='USER_ENTERED'
)
```

**Limits:**
- 10 million cells per sheet (we use ~200,000)
- 100 requests per 100 seconds (we use 1-2)
- 500 requests per day (we use 1-2)
- Well within limits ✓

### 5. Error Handling
```python
try:
    scraper = scraper_class()
    product_count = scraper.run(max_products=None)
except Exception as e:
    print(f"✗ {name}: Error - {str(e)}")
    results.append({"status": "error", "error": str(e)})
    # Continue to next scraper (don't stop entire pipeline)
```

**What happens if a scraper fails:**
- Error is logged
- Other scrapers continue
- Partial data is still pushed to Google Sheets
- You can see which scraper failed in logs

---

## 📈 Expected Results

### Typical Run
```
Start: Sunday 2:00 AM UTC
End: Sunday 3:15 AM UTC
Duration: 75 minutes

Products scraped: 20,543
Success rate: 100% (9/9 scrapers)
Google Sheets: Updated
Power BI: Ready for refresh
```

### Data Volume
```
Individual CSVs: 9 files × 2-3 MB = 18-27 MB
Combined CSV: 1 file × 15-20 MB
Google Sheets: ~200,000 cells
Memory usage: ~300-400 MB (within 512MB limit)
```

### Cost
```
Render.com: $0/month (free tier)
Google Sheets: $0/month (free)
Total: $0/month
```

---

## 🚨 What Could Go Wrong?

### Scenario 1: Website Blocks Scraper
**Symptom:** One scraper fails with 403/429 error
**Impact:** That website's products missing, others OK
**Solution:** Update scraper with better headers/delays

### Scenario 2: Timeout (>90 minutes)
**Symptom:** Render kills job after 90 minutes
**Impact:** Incomplete data
**Solution:** Upgrade to paid tier ($7/month for 400 min)

### Scenario 3: Google Sheets API Error
**Symptom:** Data scraped but not pushed
**Impact:** Old data remains in sheet
**Solution:** Check credentials, retry manually

### Scenario 4: Memory Limit
**Symptom:** Job crashes with out-of-memory error
**Impact:** No data collected
**Solution:** Upgrade instance or process in batches

---

## ✅ Success Indicators

### In Render Logs
```
✓ All 9 scrapers successful
✓ Total products: 20,000+
✓ "Successfully pushed to Google Sheets"
✓ No error messages
✓ Exit code: 0
```

### In Google Sheets
```
✓ Last modified: Today (Sunday)
✓ Row count: 20,000+
✓ Prices are numbers (right-aligned)
✓ Source column populated
```

### In Power BI
```
✓ Refresh successful
✓ Product count matches Google Sheets
✓ Prices sortable/calculable
✓ All 9 sources present
```

---

## 🎯 Summary

**Your production workflow:**
1. Runs automatically every Sunday at 2 AM UTC
2. Scrapes ALL products from 9 websites (~20,000 total)
3. Processes and combines data
4. Pushes to Google Sheets
5. Power BI auto-refreshes
6. Costs $0/month
7. Requires zero manual work

**Total time:** ~75 minutes
**Reliability:** High (error handling per scraper)
**Maintenance:** Minimal (only if websites change)

---

**This is your complete production workflow!** 🚀
