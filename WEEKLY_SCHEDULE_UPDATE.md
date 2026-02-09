# Weekly Schedule Update Summary

## Changes Made

The automated scraper schedule has been updated from **daily** to **weekly** execution.

---

## Updated Files

### 1. **setup_cron.sh** (Linux/Mac)
- **Old**: Runs daily at midnight (`0 0 * * *`)
- **New**: Runs every Sunday at midnight (`0 0 * * 0`)

### 2. **setup_windows_task.ps1** (Windows)
- **Old**: Daily trigger at midnight
- **New**: Weekly trigger on Sunday at midnight

### 3. **CRON_SETUP.md**
- Updated documentation to reflect weekly schedule
- Updated examples and instructions

### 4. **WINDOWS_SETUP.md**
- Updated documentation to reflect weekly schedule
- Updated setup instructions

---

## New Schedule

### Linux/Mac (Cron)
```bash
0 0 * * 0  # Every Sunday at midnight (00:00)
```

### Windows (Task Scheduler)
```
Weekly on Sunday at 00:00
```

---

## How to Apply Changes

### For Linux/Mac:

1. Run the updated setup script:
```bash
./setup_cron.sh
```

2. When prompted, choose to replace the existing cron job

3. Verify:
```bash
crontab -l
```

### For Windows:

1. Open PowerShell as Administrator

2. Navigate to project directory:
```powershell
cd C:\Users\ahmed\Desktop\scrapers
```

3. Run the updated setup script:
```powershell
.\setup_windows_task.ps1
```

4. When prompted, choose to replace the existing task

5. Verify in Task Scheduler (`taskschd.msc`)

---

## Schedule Options

### Common Weekly Schedules:

**Sunday at midnight:**
- Cron: `0 0 * * 0`
- Windows: `-Weekly -DaysOfWeek Sunday -At "00:00"`

**Monday at midnight:**
- Cron: `0 0 * * 1`
- Windows: `-Weekly -DaysOfWeek Monday -At "00:00"`

**Sunday at 2 AM:**
- Cron: `0 2 * * 0`
- Windows: `-Weekly -DaysOfWeek Sunday -At "02:00"`

**Twice weekly (Sunday and Wednesday):**
- Cron: `0 0 * * 0,3`
- Windows: `-Weekly -DaysOfWeek Sunday,Wednesday -At "00:00"`

### To Change Back to Daily:

**Daily at midnight:**
- Cron: `0 0 * * *`
- Windows: `-Daily -At "00:00"`

---

## Why Weekly?

Weekly scraping is suitable when:
- ✓ Product data doesn't change frequently
- ✓ Reduces server load on target websites
- ✓ Saves computational resources
- ✓ Sufficient for most business needs
- ✓ Reduces risk of being blocked

---

## Current Scrapers Included

All scrapers will run weekly:

1. meinhausshop
2. heima24
3. sanundo
4. heizungsdiscount24
5. wolfonlineshop
6. st_shop24
7. selfio
8. pumpe24
9. wasserpumpe
10. **wolf_online_shop** (NEW - 1,240 products)

---

## Manual Execution

You can still run scrapers manually anytime:

### All scrapers:
```bash
python run_all_scrapers_parallel.py
```

### Single scraper:
```bash
python wolf_online_shop_scraper.py --push-to-sheets
```

---

## Monitoring

### Check Next Run Time:

**Linux/Mac:**
```bash
crontab -l
```

**Windows:**
```powershell
Get-ScheduledTask -TaskName "WebScrapers-NightlyRun" | Get-ScheduledTaskInfo
```

### View Logs:

**Cron logs:**
```bash
ls -la cron_logs/
```

**Individual scraper logs:**
```bash
ls -la logs/
```

**Windows scheduled task logs:**
```bash
ls -la scheduled_logs/
```

---

## Troubleshooting

### Task not running?

1. **Verify task exists:**
   - Linux/Mac: `crontab -l`
   - Windows: Open Task Scheduler

2. **Check logs:**
   - Look in `cron_logs/` or `scheduled_logs/`
   - Check individual scraper logs in `logs/`

3. **Test manually:**
   ```bash
   python run_all_scrapers_parallel.py
   ```

### Need to change schedule?

1. Edit the setup script (`setup_cron.sh` or `setup_windows_task.ps1`)
2. Modify the trigger/schedule line
3. Run the setup script again

---

## Summary

✅ Schedule changed from daily to weekly  
✅ Runs every Sunday at midnight  
✅ All documentation updated  
✅ Both Linux/Mac and Windows scripts updated  
✅ Easy to customize schedule if needed  

The scrapers will now run automatically every Sunday at midnight, scraping all products and pushing to Google Sheets.
