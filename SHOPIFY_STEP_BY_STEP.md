# Shopify Automation - Step by Step Guide

## 🎯 Goal
Automatically sync scraped products to Shopify every week with zero manual work.

---

## 📋 STEP 1: Test CSV Conversion (5 minutes)

### What to do:
```bash
python shopify_csv_export.py 20
```

### Expected behavior:
```
Converting 10 scrapers to Shopify format...

Converting heima24...
✓ Converted 150 products
✓ Saved to: shopify_imports/heima24_shopify.csv

Converting meinhausshop...
✓ Converted 200 products
✓ Saved to: shopify_imports/meinhausshop_shopify.csv

... (continues for all scrapers)

============================================================
Conversion complete!
Output directory: shopify_imports/
Files created: 10
============================================================

📋 Next Steps:
1. Go to Shopify Admin → Products
2. Click 'Import' button
3. Upload the CSV files from shopify_imports/ folder
4. Review imported products
5. Publish when ready
```

### What it creates:
- Folder: `shopify_imports/`
- Files: `heima24_shopify.csv`, `meinhausshop_shopify.csv`, etc.
- Each CSV has products in Shopify format with 20% markup

### ✅ Success check:
- You see "Conversion complete!"
- `shopify_imports/` folder exists with CSV files
- Open a CSV file - you should see Shopify columns (Handle, Title, Vendor, etc.)

---

## 📋 STEP 2: Test Google Drive Upload (5 minutes)

### What to do:
```bash
python upload_to_drive.py
```

### Expected behavior:
```
2026-02-02 10:00:00 - INFO - ✓ Connected to Google Drive

Uploading 10 files to Google Drive...

Updating: heima24_shopify.csv
✓ Uploaded: heima24_shopify.csv
  Download URL: https://drive.google.com/uc?export=download&id=ABC123...

Updating: meinhausshop_shopify.csv
✓ Uploaded: meinhausshop_shopify.csv
  Download URL: https://drive.google.com/uc?export=download&id=DEF456...

... (continues for all files)

✓ Upload complete! 10 files uploaded
✓ URLs saved to: shopify_imports/drive_urls.txt

============================================================
✓ Files uploaded successfully!
============================================================

Next steps:
1. Open shopify_imports/drive_urls.txt
2. Copy the download URLs
3. Configure Matrixify to import from these URLs
4. Set schedule: Weekly on Sunday at 2 AM

Done! Your Shopify store will auto-update weekly.
```

### What it creates:
- Folder in Google Drive: `Shopify_Imports/`
- All CSV files uploaded to that folder
- File: `shopify_imports/drive_urls.txt` with download links

### ✅ Success check:
- You see "✓ Files uploaded successfully!"
- Open `shopify_imports/drive_urls.txt` - you should see URLs like:
  ```
  heima24:
    https://drive.google.com/uc?export=download&id=ABC123...
  
  meinhausshop:
    https://drive.google.com/uc?export=download&id=DEF456...
  ```
- Go to Google Drive - you should see `Shopify_Imports` folder with CSV files

---

## 📋 STEP 3: Install Matrixify App (5 minutes)

### What to do:
1. Go to **Shopify App Store**: https://apps.shopify.com/
2. Search for **"Matrixify"**
3. Click **"Add app"**
4. Click **"Install app"**
5. Grant permissions

### Expected behavior:
- Matrixify app appears in your Shopify admin sidebar
- You see "Welcome to Matrixify" screen
- 7-day free trial starts automatically

### ✅ Success check:
- Matrixify appears in Shopify admin → Apps
- You can open Matrixify app
- You see Import/Export options

---

## 📋 STEP 4: Configure Matrixify Scheduled Import (10 minutes)

### What to do:

**For EACH scraper** (heima24, meinhausshop, etc.):

1. Open **Matrixify app** in Shopify
2. Click **"Import"** tab
3. Click **"Schedule"** button
4. Click **"Create new schedule"**
5. Fill in the form:

   **Schedule Name**: `heima24 Weekly Import`
   
   **Import Type**: Select `Products`
   
   **Import Source**: Select `From URL`
   
   **URL**: Paste from `shopify_imports/drive_urls.txt`
   ```
   https://drive.google.com/uc?export=download&id=ABC123...
   ```
   
   **Schedule**: 
   - Frequency: `Weekly`
   - Day: `Sunday`
   - Time: `02:00 AM`
   
   **Options**:
   - ☑ Update existing products
   - Match by: `SKU`
   - ☐ Publish products (leave unchecked - review first)
   
6. Click **"Save schedule"**
7. Repeat for all scrapers (10 total)

### Expected behavior:
- Each schedule appears in Matrixify → Import → Schedules
- Status shows "Active"
- Next run time shows "Sunday 02:00 AM"

### ✅ Success check:
- You have 10 scheduled imports (one per scraper)
- All show status "Active"
- All show next run: "Sunday 02:00 AM"

---

## 📋 STEP 5: Test Full Automation (30 minutes)

### What to do:
```bash
python run_scrapers_and_sync_shopify.py
```

### Expected behavior:
```
============================================================
SHOPIFY AUTOMATION - COMPLETE WORKFLOW
============================================================
Started: 2026-02-02 10:00:00

📊 STEP 1: Running scrapers...
============================================================
Running all scrapers
============================================================
2026-02-02 10:00:05 - heima24 - INFO - Starting scraper...
2026-02-02 10:05:30 - heima24 - INFO - Completed: 150 products
... (continues for all scrapers - takes ~30 minutes)

📋 STEP 2: Converting to Shopify CSV format...
============================================================
Converting with 20% markup
============================================================
Converting heima24...
✓ Converted 150 products
... (continues for all scrapers)

☁️ STEP 3: Uploading to Google Drive...
============================================================
Uploading CSVs to Google Drive
============================================================
✓ Connected to Google Drive
Uploading 10 files to Google Drive...
✓ Upload complete! 10 files uploaded

============================================================
✓ AUTOMATION COMPLETE!
============================================================
Duration: 35.2 minutes

What happened:
  1. ✓ Scrapers ran and collected product data
  2. ✓ Data converted to Shopify CSV format
  3. ✓ CSVs uploaded to Google Drive

Next:
  → Matrixify will import from Drive URLs (scheduled)
  → Products will appear in Shopify
  → Review and publish products

============================================================
```

### What it does:
1. Runs all scrapers (saves to `data/*.csv`)
2. Converts to Shopify format (saves to `shopify_imports/*_shopify.csv`)
3. Uploads to Google Drive (updates existing files)

### ✅ Success check:
- You see "✓ AUTOMATION COMPLETE!"
- `data/` folder has fresh CSV files (today's date)
- `shopify_imports/` folder has Shopify CSV files
- Google Drive has updated files (check timestamps)

---

## 📋 STEP 6: Verify Matrixify Import (Next Sunday)

### What to do:
Wait until Sunday 02:00 AM, then check:

1. Open **Matrixify app** in Shopify
2. Go to **"History"** tab
3. Look for import jobs from today

### Expected behavior:
```
Import History:

heima24 Weekly Import
  Status: ✓ Completed
  Date: Sunday 02:05 AM
  Products: 150 imported, 0 failed
  
meinhausshop Weekly Import
  Status: ✓ Completed
  Date: Sunday 02:10 AM
  Products: 200 imported, 0 failed

... (all 10 scrapers)
```

### What it does:
- Matrixify downloads CSV from Google Drive
- Imports products to Shopify
- Matches existing products by SKU
- Updates prices for existing products
- Creates new products as drafts

### ✅ Success check:
- All imports show "✓ Completed"
- No errors in import logs
- Products appear in Shopify Admin → Products
- Products are in "Draft" status (not published)

---

## 📋 STEP 7: Review and Publish Products

### What to do:
1. Go to **Shopify Admin** → **Products**
2. Filter by: **Status = Draft**
3. Review products:
   - Check titles, prices, images
   - Verify manufacturer and category
   - Check SKU and EAN
4. Select products to publish
5. Click **"Publish"** → **"Publish to Online Store"**

### Expected behavior:
- You see all imported products
- Products have correct data from scrapers
- Prices include 20% markup
- Images are loaded
- Products are organized by vendor/category

### ✅ Success check:
- Products look correct
- Prices are right (original + 20%)
- Images display properly
- Published products appear on your store

---

## 📋 STEP 8: Schedule Weekly Automation

### Windows (Task Scheduler):

1. Open **Task Scheduler**
2. Click **"Create Basic Task"**
3. Name: `Shopify Automation`
4. Trigger: **Weekly**, **Sunday**, **12:00 AM**
5. Action: **Start a program**
   - Program: `python`
   - Arguments: `run_scrapers_and_sync_shopify.py`
   - Start in: `C:\Users\ahmed\Desktop\scrapers`
6. Click **Finish**

### Expected behavior:
- Task appears in Task Scheduler
- Status: "Ready"
- Next run time: "Next Sunday 12:00 AM"

### ✅ Success check:
- Task is created and enabled
- Shows correct schedule
- Test run: Right-click → Run → Check if it works

---

## 🎉 FINAL RESULT

### Weekly Automation Flow:

```
Sunday 00:00 AM → Windows Task triggers
Sunday 00:05 AM → Scrapers start
Sunday 00:35 AM → Scrapers finish
Sunday 00:36 AM → Convert to Shopify CSV
Sunday 00:37 AM → Upload to Google Drive
Sunday 00:38 AM → Automation script completes

Sunday 02:00 AM → Matrixify imports (scheduled)
Sunday 02:30 AM → All products imported to Shopify

Monday morning → You review and publish new products
```

### What You Do:
- **Nothing!** It runs automatically
- Monday: Spend 5 minutes reviewing new products
- Publish approved products
- Done!

---

## 🔍 Troubleshooting

### Problem: "Drive upload failed"
**Check:**
- `credentials/credentials.json` exists
- Google Drive API is enabled
- Run: `python upload_to_drive.py` to see error

### Problem: "Matrixify not importing"
**Check:**
- Drive URLs are public (test in browser)
- Schedule is enabled in Matrixify
- Check Matrixify → History for errors

### Problem: "Products not updating prices"
**Check:**
- "Update existing products" is enabled
- Matching by SKU is selected
- SKUs match between CSV and Shopify

### Problem: "Scrapers failing"
**Check:**
- Individual scraper logs in `logs/`
- Run scrapers manually to debug
- Some sites may be temporarily down

---

## 📊 Summary

**Setup Time**: 30 minutes (one-time)
**Weekly Time**: 5 minutes (review products)
**Automation Level**: 100%
**Monthly Cost**: $30 (Matrixify)

**What's Automated:**
✅ Scraping products
✅ Converting to Shopify format
✅ Uploading to Google Drive
✅ Importing to Shopify
✅ Updating prices
✅ Creating new products

**What You Do:**
- Review new products (5 min/week)
- Publish approved products
- That's it!

---

## 🚀 Quick Start Commands

```bash
# Test CSV conversion
python shopify_csv_export.py 20

# Test Drive upload
python upload_to_drive.py

# Test full automation
python run_scrapers_and_sync_shopify.py

# Check what will be uploaded
cat shopify_imports/drive_urls.txt
```

---

## ✅ Success Checklist

- [ ] CSV conversion works
- [ ] Google Drive upload works
- [ ] Matrixify app installed
- [ ] 10 scheduled imports configured
- [ ] Full automation tested
- [ ] Products appear in Shopify
- [ ] Weekly task scheduled
- [ ] First import successful

**When all checked → You're done! 🎉**
