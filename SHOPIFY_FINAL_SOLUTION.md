# Shopify Integration - Final Solution

## ✅ Your Current Flow

```
Week 1: Scrapers run → Push to Google Sheets
Week 2: Scrapers run → Push to Google Sheets
...
```

## ✅ New Automated Flow

```
Week 1: 
  Sunday 2 AM: Scrapers run → Push to Google Sheets
  Sunday 4 AM: Shopify sync runs → Pull from Sheets → Upload to Shopify

Week 2:
  Sunday 2 AM: Scrapers run → Push to Google Sheets  
  Sunday 4 AM: Shopify sync runs → Pull from Sheets → Upload to Shopify
...
```

## 🚀 Setup (One Time Only)

### Step 1: Install Selenium
```bash
pip install selenium
```

### Step 2: Set up the Shopify sync task
```powershell
# Run as Administrator
.\setup_shopify_sync_task.ps1 -ShopifyEmail "admin@tbbt.de" -ShopifyPassword "yourpassword"
```

That's it! The task will run 2 hours after your scrapers finish.

## 📋 What Happens Automatically

**Every Sunday at 4 AM:**

1. **Download from Google Sheets** - Gets latest data from all your sheets
2. **Convert to Shopify CSV** - Adds 20% markup, formats for Shopify
3. **Upload to Shopify** - Selenium logs in and uploads automatically
4. **Products imported** - All products added as drafts for review

## ⚙️ Configuration

### Change the delay
If your scrapers take longer than 2 hours:
```powershell
.\setup_shopify_sync_task.ps1 -ShopifyEmail "admin@tbbt.de" -ShopifyPassword "yourpass" -DelayHours 3
```

### Change price markup
Edit `shopify_sync_from_sheets.py`, line with:
```python
convert_to_shopify_format(markup_percent=20)  # Change 20 to your %
```

### Run manually (for testing)
```bash
python shopify_sync_from_sheets.py admin@tbbt.de yourpassword 20
```

## 🔒 Security

Store credentials securely using environment variables:
```powershell
# Set once
[System.Environment]::SetEnvironmentVariable('SHOPIFY_EMAIL', 'admin@tbbt.de', 'User')
[System.Environment]::SetEnvironmentVariable('SHOPIFY_PASSWORD', 'yourpassword', 'User')

# Then setup task without exposing password
.\setup_shopify_sync_task.ps1 -ShopifyEmail $env:SHOPIFY_EMAIL -ShopifyPassword $env:SHOPIFY_PASSWORD
```

## 📊 Monitoring

### Check if task ran
```powershell
Get-ScheduledTask -TaskName "Shopify_Sync_After_Scrapers" | Get-ScheduledTaskInfo
```

### View task history
1. Open Task Scheduler (`taskschd.msc`)
2. Find "Shopify_Sync_After_Scrapers"
3. Click "History" tab

### Check logs
Logs are saved in the console output when task runs.

## 🛠️ Managing the Task

**Run manually:**
```powershell
Start-ScheduledTask -TaskName "Shopify_Sync_After_Scrapers"
```

**Disable:**
```powershell
Disable-ScheduledTask -TaskName "Shopify_Sync_After_Scrapers"
```

**Remove:**
```powershell
Unregister-ScheduledTask -TaskName "Shopify_Sync_After_Scrapers" -Confirm:$false
```

## ✨ Benefits

- ✅ **Fully automated** - No human involvement needed
- ✅ **Works with your existing flow** - Just adds Shopify sync
- ✅ **No API tokens** - Uses Selenium with your login
- ✅ **Safe** - Products imported as drafts
- ✅ **Flexible** - Easy to adjust timing and settings

## 🎯 Complete Weekly Flow

```
Sunday 2:00 AM - Your existing scraper task runs
                  ↓
                  Scrapes 18 websites
                  ↓
                  Pushes to Google Sheets
                  ↓
                  (2 hour wait)
                  ↓
Sunday 4:00 AM - New Shopify sync task runs
                  ↓
                  Downloads from Google Sheets
                  ↓
                  Converts to Shopify CSV (20% markup)
                  ↓
                  Uploads to Shopify via Selenium
                  ↓
                  ✓ Done! Products in Shopify as drafts
```

## 📝 Files Created

- `shopify_sync_from_sheets.py` - Main sync script
- `shopify_selenium_uploader.py` - Selenium uploader
- `setup_shopify_sync_task.ps1` - Task setup script
- `run_full_automation.py` - Alternative all-in-one script

## 🎬 You're All Set!

Just run the setup command once and forget about it. Your products will automatically sync to Shopify every week!

```powershell
.\setup_shopify_sync_task.ps1 -ShopifyEmail "admin@tbbt.de" -ShopifyPassword "yourpassword"
```

---

**Status:** ✅ Ready for full automation
**Method:** Selenium-based (no API tokens)
**Schedule:** Weekly, 2 hours after scrapers
**Products:** 33,000+ ready to sync
