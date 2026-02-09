# Complete Project Flow - End-to-End Explanation

## 🎯 Project Overview

You're scraping product data from 18 German e-commerce websites and making it available in multiple formats: Google Sheets, Power BI, and now Shopify.

---

## 📊 THE COMPLETE WEEKLY FLOW

### **Sunday 2:00 AM - Data Collection**

**What Happens:**
```
Windows Task Scheduler triggers: "WebScrapers-NightlyRun"
↓
Runs: run_all_scrapers_sequential.py
↓
Executes 18 individual scrapers in sequence
```

**The 18 Scrapers:**
1. actec_scraper.py
2. akusolar_scraper.py
3. alpha_scraper.py
4. czech_scraper.py
5. erneuerbar_scraper.py
6. glo24_scraper.py
7. heima24_scraper.py (24,484 products - largest)
8. heizungsdiscount24_scraper.py (4,589 products)
9. meinhausshop_scraper.py (500 products)
10. priwatt_scraper.py
11. pumpe24_scraper.py
12. sanundo_scraper.py
13. selfio_scraper.py
14. st_shop24_scraper.py
15. wasserpumpe_scraper.py
16. wolfonlineshop_scraper.py
17. wolf_online_shop_scraper.py (1,243 products)
18. zendure_scraper.py

**What Each Scraper Does:**
1. Visits the target website
2. Extracts product data:
   - Product name
   - Article number (SKU)
   - EAN/barcode
   - Price (gross and net)
   - Manufacturer
   - Category
   - Product image URL
   - Product page URL
3. Saves to CSV: `data/{scraper_name}.csv`
4. Pushes to Google Sheets (using `google_sheets_helper.py`)
5. Logs activity to: `logs/{scraper_name}.log`

**Total Products Scraped:** ~31,488 products

**Duration:** ~2 hours (depends on website response times)

---

### **Sunday 4:00 AM - Shopify Export**

**What Happens:**
```
Windows Task Scheduler triggers: "Weekly_Shopify_CSV_Export"
↓
Runs: shopify_csv_export.py 20
↓
Converts all CSV files to Shopify format
```

**Conversion Process:**
1. Reads all CSV files from `data/` folder
2. For each product:
   - Applies 20% price markup
   - Converts to Shopify CSV format with required columns:
     * Handle (URL-friendly ID)
     * Title
     * Body (HTML description)
     * Vendor (manufacturer)
     * Type (category)
     * Variant SKU (article number)
     * Variant Barcode (EAN)
     * Variant Price (with markup)
     * Image Src (product image)
     * Status (draft - not published)
3. Saves to: `shopify_imports/{scraper_name}_shopify.csv`

**Output:** 16 Shopify-ready CSV files (31,488 products)

**Duration:** ~1 minute

---

### **Monday Morning - Distribution**

**Current State:**
- CSV files in `data/` folder (raw scraped data)
- CSV files in `shopify_imports/` folder (Shopify-ready)
- Data in Google Sheets (19 sheets, one per scraper)

**What You Do:**

**Option 1: Manual (Current)**
- Zip `shopify_imports/` folder
- Send to client
- Client imports manually in Shopify Admin

**Option 2: Matrixify (Recommended)**
- Upload CSVs to Dropbox/Google Drive
- Get public URLs
- Client's Matrixify app auto-imports from URLs
- 100% automated

---

## 🏗️ SYSTEM ARCHITECTURE

### **Layer 1: Data Collection**

```
18 Websites
    ↓
Base Scraper Class (base_scraper.py)
    ↓
Individual Scrapers (e.g., heima24_scraper.py)
    ↓
Techniques Used:
- requests + BeautifulSoup (most sites)
- Selenium (for JavaScript-heavy sites)
- cloudscraper (for Cloudflare protection)
- undetected_chromedriver (for bot detection)
```

### **Layer 2: Data Storage**

```
Scraped Data
    ↓
    ├─→ Local CSV (data/*.csv)
    ├─→ Google Sheets (via google_sheets_helper.py)
    └─→ Logs (logs/*.log)
```

### **Layer 3: Data Transformation**

```
Raw CSV Data
    ↓
shopify_csv_export.py
    ↓
- Apply price markup (20%)
- Convert to Shopify format
- Generate product descriptions
- Create URL-friendly handles
    ↓
Shopify CSV Files (shopify_imports/*.csv)
```

### **Layer 4: Distribution**

```
Shopify CSV Files
    ↓
    ├─→ Manual: Zip & send to client
    ├─→ Matrixify: Upload to cloud, auto-import
    └─→ Future: Direct API integration (if credentials available)
```

---

## 📁 KEY FILES & THEIR ROLES

### **Core Scraping**
- `base_scraper.py` - Base class with common scraping logic
- `{site}_scraper.py` - Individual scrapers for each website
- `run_all_scrapers_sequential.py` - Runs all scrapers in order
- `run_all_scrapers_parallel.py` - Runs scrapers in parallel (faster)

### **Configuration**
- `config.py` - Google Sheets IDs, scraper settings
- `credentials/credentials.json` - Google API credentials
- `requirements.txt` - Python dependencies

### **Data Management**
- `google_sheets_helper.py` - Push/pull data to Google Sheets
- `create_sheets.py` - Create new Google Sheets for scrapers

### **Shopify Integration**
- `shopify_csv_export.py` - Convert to Shopify CSV format
- `shopify_imports/` - Output folder for Shopify CSVs

### **Automation**
- Windows Task Scheduler tasks:
  - `WebScrapers-NightlyRun` (Sunday 2 AM)
  - `Weekly_Shopify_CSV_Export` (Sunday 4 AM)

### **Monitoring**
- `logs/` - Scraper execution logs
- `email_notifier.py` - Send email notifications (optional)

---

## 🔄 DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                    SUNDAY 2:00 AM                           │
│                  Scrapers Start Running                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  18 Websites Scraped                        │
│  heima24.de, heizungsdiscount24.de, wolf-online-shop.de...  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Product Data Extracted                         │
│  Name, SKU, EAN, Price, Manufacturer, Category, Image...   │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────┴───────┐
                    ↓               ↓
        ┌───────────────┐   ┌──────────────┐
        │  Local CSV    │   │ Google Sheets│
        │  data/*.csv   │   │  19 Sheets   │
        └───────────────┘   └──────────────┘
                    │               │
                    └───────┬───────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    SUNDAY 4:00 AM                           │
│              Shopify Export Triggered                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              shopify_csv_export.py                          │
│  - Read all CSV files                                       │
│  - Apply 20% markup                                         │
│  - Convert to Shopify format                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           Shopify CSV Files Generated                       │
│        shopify_imports/*_shopify.csv                        │
│           31,488 products ready                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────┴───────┐
                    ↓               ↓
        ┌───────────────┐   ┌──────────────────┐
        │  Manual Send  │   │  Matrixify Auto  │
        │  to Client    │   │  Import (Future) │
        └───────────────┘   └──────────────────┘
                    │               │
                    └───────┬───────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Shopify Store                              │
│              Products Imported as Drafts                    │
│           Client Reviews & Publishes                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎛️ CONTROL POINTS

### **Where You Can Intervene:**

1. **Change Scraping Schedule**
   - Edit Windows Task: `WebScrapers-NightlyRun`
   - Default: Sunday 2 AM

2. **Change Export Schedule**
   - Edit Windows Task: `Weekly_Shopify_CSV_Export`
   - Default: Sunday 4 AM

3. **Change Price Markup**
   - Edit task command: `shopify_csv_export.py 20` → change `20` to desired %
   - Or run manually: `python shopify_csv_export.py 25`

4. **Run Scrapers Manually**
   - All: `python run_all_scrapers_sequential.py`
   - Single: `python heima24_scraper.py`

5. **Generate Shopify CSVs Manually**
   - `python shopify_csv_export.py 20`

6. **Check Logs**
   - View: `logs/{scraper_name}.log`
   - Check for errors, product counts, timing

---

## 📈 CURRENT STATISTICS

### **Data Volume:**
- Total products: ~31,488
- Largest scraper: heima24 (24,484 products)
- Smallest scraper: czech (3 products)
- Active scrapers: 16 out of 18

### **Automation:**
- Scraping: ✅ Fully automated (weekly)
- Google Sheets sync: ✅ Fully automated
- Shopify CSV export: ✅ Fully automated
- Shopify import: ⚠️ Manual (or Matrixify)

### **Performance:**
- Scraping duration: ~2 hours
- CSV export duration: ~1 minute
- Total weekly runtime: ~2 hours 1 minute

---

## 🚀 FUTURE ENHANCEMENTS

### **Possible Improvements:**

1. **Full Shopify Automation**
   - Option A: Client provides Shopify credentials
   - Option B: Client installs Matrixify app
   - Option C: Upload to cloud storage, Matrixify imports

2. **Real-time Monitoring**
   - Email notifications on scraper failures
   - Dashboard showing scraper status
   - Alerts for price changes

3. **Data Quality**
   - Duplicate detection
   - Price validation
   - Image availability checks

4. **Performance**
   - Parallel scraping (already available)
   - Incremental updates (only changed products)
   - Caching for faster re-runs

---

## 🎯 SUMMARY

**What You Have:**
- 18 automated web scrapers
- Weekly data collection (Sunday 2 AM)
- Automatic Google Sheets sync
- Automatic Shopify CSV generation (Sunday 4 AM)
- 31,488 products ready for Shopify

**What's Automated:**
- ✅ Data scraping
- ✅ CSV storage
- ✅ Google Sheets sync
- ✅ Shopify CSV export
- ⚠️ Shopify import (needs client or Matrixify)

**Your Weekly Work:**
- Option 1: Send CSV files to client (5 minutes)
- Option 2: Upload to cloud for Matrixify (5 minutes)
- Option 3: Nothing (if Matrixify is set up)

**Client's Work:**
- Option 1: Import CSVs manually in Shopify (30 minutes)
- Option 2: Nothing (if Matrixify is set up)

---

## 📞 QUICK REFERENCE

**Run scrapers now:**
```bash
python run_all_scrapers_sequential.py
```

**Generate Shopify CSVs now:**
```bash
python shopify_csv_export.py 20
```

**Check scheduled tasks:**
```bash
schtasks /query /tn "WebScrapers-NightlyRun"
schtasks /query /tn "Weekly_Shopify_CSV_Export"
```

**View logs:**
```bash
type logs\heima24.log
```

**Test single scraper:**
```bash
python heima24_scraper.py
```

---

That's the complete flow! Everything is automated except the final step of getting files into Shopify, which requires either manual work or the Matrixify app.
