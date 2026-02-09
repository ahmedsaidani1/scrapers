# Power BI Automatic Setup Guide

## Overview
This guide shows how to set up Power BI to automatically refresh data from Google Sheets **without any manual intervention** each week.

## One-Time Setup (Client Does This Once)

### Step 1: Get the Data Source URL

Use this CSV export URL (it automatically updates when the Google Sheet updates):
```
https://docs.google.com/spreadsheets/d/1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA/export?format=csv
```

**Why CSV export URL?**
- Headers are automatically recognized
- Numbers are automatically detected as numbers (sortable)
- No manual transformation needed
- Works with automatic refresh

### Step 2: Import into Power BI Desktop

1. **Open Power BI Desktop**

2. **Get Data from Web**
   - Click "Home" → "Get Data" → "Web"
   - Paste the CSV export URL above
   - Click "OK"

3. **Load the Data**
   - Power BI will show a preview
   - You should see:
     - ✅ Column names: manufacturer, category, name, title, article_number, price_net, price_gross, ean, product_image, product_url, source
     - ✅ price_net and price_gross showing as numbers (with Σ icon)
   - Click "Load" (no transformation needed!)

4. **Verify the Data**
   - Check that all 11 columns are visible with correct names
   - Click on price_gross column header to sort - it should sort numerically
   - Create a simple visualization to test

### Step 3: Set Up Automatic Refresh

#### For Power BI Desktop (Local Files)

1. **Configure Data Source**
   - Go to "Home" → "Transform Data" → "Data Source Settings"
   - Verify the URL is correct
   - Click "Close"

2. **Manual Refresh**
   - Click "Home" → "Refresh"
   - This will pull the latest data from Google Sheets
   - Do this weekly after the scraper runs

#### For Power BI Service (Cloud - Recommended)

1. **Publish to Power BI Service**
   - Click "Home" → "Publish"
   - Select your workspace
   - Click "Select"

2. **Configure Scheduled Refresh**
   - Go to PowerBI.com
   - Find your dataset
   - Click "..." → "Settings"
   - Under "Scheduled refresh":
     - Turn on "Keep your data up to date"
     - Set frequency: Weekly
     - Set time: After your scraper runs (e.g., Monday 9:00 AM)
     - Add time zone
   - Click "Apply"

3. **Done!**
   - Power BI will automatically refresh every week
   - No manual intervention needed

## Weekly Workflow (Automated)

### What Happens Automatically:

1. **Sunday Night**: Your scraper runs (scheduled task)
   - Scrapes 9 websites
   - Converts prices to numbers
   - Pushes to Google Sheets

2. **Monday Morning**: Power BI refreshes (scheduled)
   - Pulls latest data from Google Sheets
   - Updates all dashboards and reports
   - Sends email notifications (if configured)

3. **Client**: Opens Power BI
   - Sees fresh data automatically
   - No manual refresh needed
   - No data transformation needed

## Troubleshooting

### Headers Not Showing
**Problem**: Columns show as Column1, Column2, etc.

**Solution**: 
- You used the wrong URL. Use the CSV export URL, not the regular Google Sheets URL
- Or in Power Query Editor: Transform → "Use First Row as Headers"

### Prices Not Sortable
**Problem**: Prices sort alphabetically (10 comes before 2)

**Solution**:
- Check that the CSV has numbers without quotes
- In Power Query Editor: Select price columns → Change Type → "Decimal Number"

### Data Not Refreshing
**Problem**: Old data still showing after scraper runs

**Solution**:
- Click "Refresh" button in Power BI Desktop
- Or check scheduled refresh settings in Power BI Service
- Verify the Google Sheet has new data

### "Unable to Connect" Error
**Problem**: Power BI can't access the Google Sheet

**Solution**:
- Make sure the Google Sheet is shared: "Anyone with the link can view"
- Check your internet connection
- Try the URL in a browser first to verify it works

## Best Practices

### For the Developer (You):
1. Run the scraper on a schedule (e.g., Sunday 11 PM)
2. Verify the Google Sheet updated successfully
3. Check the logs for any errors
4. Send a notification email when complete

### For the Client:
1. Set up Power BI Service scheduled refresh (one-time)
2. Create dashboards and reports (one-time)
3. Just open Power BI to see fresh data (weekly)
4. No manual work required!

## Testing the Setup

### Test 1: Initial Load
1. Follow Step 2 above to import data
2. Verify all columns and data types are correct
3. Create a simple table visualization
4. Sort by price_gross - should sort numerically

### Test 2: Refresh
1. Make a small change to the Google Sheet manually
2. In Power BI, click "Refresh"
3. Verify the change appears
4. This confirms automatic refresh will work

### Test 3: Scheduled Refresh (Power BI Service only)
1. Publish to Power BI Service
2. Configure scheduled refresh
3. Wait for the scheduled time
4. Check that data updated automatically

## Summary

✅ **One-time setup**: Client imports data using CSV export URL  
✅ **Automatic refresh**: Power BI pulls new data weekly  
✅ **No manual work**: Headers and data types are automatic  
✅ **Fully automated**: Scraper → Google Sheets → Power BI → Dashboard

The client only needs to open Power BI to see the latest data. Everything else is automatic!
