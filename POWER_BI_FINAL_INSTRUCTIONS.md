# Power BI Setup - ONE TIME ONLY

## The Problem
Power BI doesn't automatically detect headers from Google Sheets CSV export. But once you tell it where the headers are, it remembers forever.

## ONE-TIME Setup (Client Does This ONCE)

### Step 1: Import Data
1. Open Power BI Desktop
2. Get Data → Web
3. Paste this URL:
   ```
   https://docs.google.com/spreadsheets/d/15SdkCMxfZvD8SdHk0LveoGQFUY4zY0okQvuMUjcmyaU/export?format=csv
   ```
4. Click OK

### Step 2: Configure Headers and Data Types (ONCE)
Power Query Editor will open. Do these steps:

1. **Use First Row as Headers**
   - Click "Transform" tab in ribbon
   - Click "Use First Row as Headers"
   - Now you see: manufacturer, category, name, title, etc.

2. **Fix Price Columns**
   - Click on `price_net` column header
   - In ribbon, click "Data Type" dropdown → "Decimal Number"
   - Click on `price_gross` column header  
   - In ribbon, click "Data Type" dropdown → "Decimal Number"

3. **Apply and Save**
   - Click "Close & Apply" (top left)
   - Save your Power BI file (.pbix)

**DONE! You never have to do this again!**

## Every Week After (100% Automatic)

### What Happens Automatically:

**Sunday Night:**
- Your scraper runs (scheduled task)
- Updates Google Sheet with new data

**Monday Morning:**
- Client opens Power BI
- Clicks "Refresh" button (or it auto-refreshes if published to Power BI Service)
- Power BI:
  - ✅ Pulls new data from Google Sheet
  - ✅ Automatically uses first row as headers
  - ✅ Automatically treats prices as numbers
  - ✅ Updates all dashboards

**No manual work needed!** The transformations you did once are saved in the Power BI file and apply automatically every time.

## Why This Works

Power BI saves your transformations in the .pbix file as "Applied Steps". Every time you refresh:
1. It downloads the CSV
2. It applies the same steps you configured once
3. Headers are recognized
4. Numbers are numbers
5. Everything just works

## Testing

After the one-time setup:
1. Make a small change to the Google Sheet manually
2. In Power BI, click "Refresh"
3. Verify the change appears
4. Verify headers are still correct
5. Verify prices are still sortable

This confirms automatic refresh works!

## Summary

✅ **One-time setup**: 5 minutes to configure headers and data types  
✅ **Saved forever**: Transformations are saved in the .pbix file  
✅ **Automatic refresh**: Just click "Refresh" to get new data  
✅ **No manual work**: Headers and data types apply automatically  

The client does the setup ONCE and then it's 100% automatic forever!
