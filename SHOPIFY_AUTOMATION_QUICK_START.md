# Shopify Automation - Quick Start Guide

## 🚀 One-Time Setup

### Step 1: Run Setup Script (as Administrator)

**Option A: Interactive Setup (Recommended)**
```powershell
# Right-click PowerShell → Run as Administrator
cd C:\Users\ahmed\Desktop\scrapers
.\setup_shopify_automation.ps1
```

The script will:
- Prompt for your Shopify email and password
- Test your Python environment
- Create the automated task
- Show you a summary

**Option B: With Test Mode**
```powershell
.\setup_shopify_automation.ps1 -TestMode
```

This will run a test sync first before setting up automation.

**Option C: Command Line (No Prompts)**
```powershell
.\setup_shopify_automation.ps1 -ShopifyEmail "admin@tbbt.de" -ShopifyPassword (ConvertTo-SecureString "yourpassword" -AsPlainText -Force)
```

### Step 2: Enable Your Scraper Task (if disabled)

```powershell
Enable-ScheduledTask -TaskName "WebScrapers-NightlyRun"
```

### Step 3: Done! 🎉

Your automation is now set up. Every Sunday:
- 2:00 AM - Scrapers run and push to Google Sheets
- 4:00 AM - Shopify sync runs automatically

---

## 📋 Configuration Options

### Change the Delay

If your scrapers take longer than 2 hours:
```powershell
.\setup_shopify_automation.ps1 -DelayHours 3
```

### Change Price Markup

Default is 20%. To change:
```powershell
.\setup_shopify_automation.ps1 -PriceMarkup 25
```

### Custom Schedule

To change when it runs, edit the task in Task Scheduler:
1. Open Task Scheduler (`taskschd.msc`)
2. Find "Shopify_Sync_After_Scrapers"
3. Right-click → Properties → Triggers → Edit

---

## 🧪 Testing

### Test the Sync Manually

```bash
# Test with your credentials
python shopify_sync_from_sheets.py admin@tbbt.de yourpassword 20
```

### Run the Scheduled Task Now

```powershell
Start-ScheduledTask -TaskName "Shopify_Sync_After_Scrapers"
```

### Check Task Status

```powershell
Get-ScheduledTask -TaskName "Shopify_Sync_After_Scrapers" | Get-ScheduledTaskInfo
```

---

## 🔍 Monitoring

### View Task History

1. Open Task Scheduler (`taskschd.msc`)
2. Find "Shopify_Sync_After_Scrapers"
3. Click "History" tab
4. Look for recent runs and any errors

### Check What Was Synced

After the task runs, check:
- `shopify_imports/` folder for generated CSV files
- Shopify Admin → Products → Filter by "Draft" status
- Look for products tagged with "imported, scraped"

---

## 🛠️ Management Commands

### Disable Automation

```powershell
Disable-ScheduledTask -TaskName "Shopify_Sync_After_Scrapers"
```

### Enable Automation

```powershell
Enable-ScheduledTask -TaskName "Shopify_Sync_After_Scrapers"
```

### Remove Automation

```powershell
Unregister-ScheduledTask -TaskName "Shopify_Sync_After_Scrapers" -Confirm:$false
```

### Re-run Setup

Just run the setup script again - it will remove the old task and create a new one.

---

## 📊 What Happens During Sync

### Step 1: Download from Google Sheets (2-3 minutes)
- Connects to your 19 configured Google Sheets
- Downloads latest product data
- Saves to `data/*.csv` files

### Step 2: Convert to Shopify Format (1 minute)
- Reads all CSV files from `data/` folder
- Applies 20% price markup (configurable)
- Converts to Shopify CSV format
- Saves to `shopify_imports/*_shopify.csv`

### Step 3: Upload to Shopify (10-30 minutes)
- Opens Chrome browser (headless mode)
- Logs into Shopify admin
- Navigates to Products → Import
- Uploads each CSV file
- Waits for import to complete
- Closes browser

### Step 4: Products in Shopify
- All products imported as **drafts**
- Tagged with "imported, scraped"
- Ready for review and publishing

---

## ⚠️ Troubleshooting

### "Login failed"
- Check your Shopify email and password
- Make sure you can login manually at admin.shopify.com
- Try running with `-TestMode` to see detailed errors

### "Chrome driver not found"
- Selenium should auto-download the driver
- If not, install manually: `python -m pip install webdriver-manager`

### "No data files found"
- Make sure your scrapers have run first
- Check that `data/*.csv` files exist
- Run scrapers manually: `python run_all_scrapers_sequential.py`

### "Google Sheets connection failed"
- Check `credentials/credentials.json` exists
- Verify Google Sheets API is enabled
- Test: `python google_sheets_helper.py`

### Task doesn't run
- Check task is enabled: `Get-ScheduledTask -TaskName "Shopify_Sync_After_Scrapers"`
- Check task history in Task Scheduler
- Make sure computer is on at scheduled time
- Check "Run whether user is logged on or not" is NOT checked

### Products not appearing in Shopify
- Check they're imported as drafts (not published)
- Look in Shopify Admin → Products → Filter: Draft
- Check for import errors in Shopify Admin → Settings → Files

---

## 🔒 Security Notes

### Credentials Storage
- Passwords are stored in the scheduled task
- Task runs under your Windows user account
- Only you can view/edit the task

### Better Security (Optional)
Use environment variables instead:

```powershell
# Set once
[System.Environment]::SetEnvironmentVariable('SHOPIFY_EMAIL', 'admin@tbbt.de', 'User')
[System.Environment]::SetEnvironmentVariable('SHOPIFY_PASSWORD', 'yourpassword', 'User')

# Then modify shopify_sync_from_sheets.py to read from env vars
```

---

## 📈 Expected Results

With 18 scrapers and ~33,000 products:
- **Download**: 2-3 minutes
- **Convert**: 1 minute  
- **Upload**: 20-40 minutes (depends on file sizes)
- **Total**: ~30-45 minutes

Products will be:
- ✅ Imported as drafts
- ✅ Tagged with "imported, scraped"
- ✅ Prices marked up by 20%
- ✅ Ready for review
- ✅ Can be published individually or in bulk

---

## 🎯 Complete Weekly Flow

```
Sunday 2:00 AM
  ↓
Scrapers run (WebScrapers-NightlyRun task)
  ↓
Scrape 18 websites
  ↓
Push to Google Sheets
  ↓
[2 hour wait]
  ↓
Sunday 4:00 AM
  ↓
Shopify sync runs (Shopify_Sync_After_Scrapers task)
  ↓
Download from Google Sheets
  ↓
Convert to Shopify CSV (20% markup)
  ↓
Upload to Shopify via Selenium
  ↓
Products imported as drafts
  ↓
✓ Done! Review in Shopify admin
```

---

## 📞 Need Help?

Check these files for more details:
- `SHOPIFY_FINAL_SOLUTION.md` - Complete solution overview
- `SHOPIFY_AUTOMATION_SOLUTION.md` - Alternative solutions
- `shopify_sync_from_sheets.py` - Main sync script
- `shopify_selenium_uploader.py` - Upload automation

---

## ✅ Quick Checklist

Before running automation:
- [ ] Scrapers are working and pushing to Google Sheets
- [ ] Google Sheets credentials are set up
- [ ] Selenium is installed (`python -m pip show selenium`)
- [ ] Chrome browser is installed
- [ ] You have Shopify admin access
- [ ] You've tested manually first

After setup:
- [ ] Task is created and enabled
- [ ] Task schedule is correct (Sunday 4 AM)
- [ ] Scraper task is enabled (Sunday 2 AM)
- [ ] You've tested the task manually
- [ ] You can see products in Shopify admin

---

**Status**: ✅ Ready for automation
**Method**: Selenium-based (no API needed)
**Schedule**: Weekly, 2 hours after scrapers
**Products**: 33,000+ ready to sync
