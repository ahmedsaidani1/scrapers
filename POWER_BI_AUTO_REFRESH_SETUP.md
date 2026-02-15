# Power BI Automatic Refresh Setup

## 🎯 Overview

There are TWO ways to set up automatic refresh in Power BI:

1. **Power BI Desktop** - Scheduled refresh on local computer (simpler, free)
2. **Power BI Service** - Cloud-based refresh (more powerful, requires Pro license)

---

## Option 1: Power BI Desktop (Local Refresh)

### ✅ Pros
- Free (no Pro license needed)
- Simple setup
- Works on your computer

### ❌ Cons
- Computer must be on and Power BI Desktop must be running
- Manual trigger or Windows Task Scheduler needed
- Not truly "automatic" unless computer always on

### Setup Steps

#### Step 1: Configure Data Source
1. Open Power BI Desktop
2. Go to **Home** → **Get Data** → **Web**
3. Enter URL:
```
https://docs.google.com/spreadsheets/d/1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg/export?format=csv
```
4. Click **OK**
5. Power BI loads the data
6. Click **Load** (not Transform)

#### Step 2: Set Refresh Options
1. Go to **File** → **Options and settings** → **Options**
2. Select **Data Load** in left menu
3. Configure:
   - ✓ Enable background data refresh
   - ✓ Allow data preview to download in background
4. Click **OK**

#### Step 3: Manual Refresh
To refresh manually:
1. Click **Home** → **Refresh** button
2. Or press **F5**
3. Data updates from Google Sheets

#### Step 4: Automate with Windows Task Scheduler (Optional)

Create a PowerShell script to open Power BI and refresh:

**File: `refresh_powerbi.ps1`**
```powershell
# Path to your Power BI file
$pbixFile = "C:\Users\YourName\Documents\PowerBI\YourDashboard.pbix"

# Open Power BI Desktop
Start-Process "C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe" -ArgumentList $pbixFile

# Wait for Power BI to open
Start-Sleep -Seconds 30

# Send F5 key to refresh (requires PowerShell 7+)
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("{F5}")

Write-Host "Power BI refresh triggered"
```

**Schedule with Task Scheduler:**
1. Open **Task Scheduler**
2. Create Basic Task
3. Name: "Power BI Auto Refresh"
4. Trigger: Weekly, Monday 9:00 AM
5. Action: Start a program
6. Program: `powershell.exe`
7. Arguments: `-File "C:\path\to\refresh_powerbi.ps1"`
8. Finish

**Limitations:**
- Computer must be on
- Power BI Desktop must be installed
- Not reliable for production use

---

## Option 2: Power BI Service (Cloud Refresh) ⭐ RECOMMENDED

### ✅ Pros
- Truly automatic (cloud-based)
- No computer needed
- Reliable and professional
- Refresh even when you're offline
- Email notifications on success/failure

### ❌ Cons
- Requires Power BI Pro license ($10/user/month)
- Or Power BI Premium ($20/user/month)
- Initial setup more complex

### Setup Steps

#### Step 1: Publish to Power BI Service

1. **In Power BI Desktop:**
   - Open your dashboard
   - Click **Home** → **Publish**
   - Sign in with your Microsoft account
   - Select workspace (e.g., "My workspace")
   - Click **Select**
   - Wait for publish to complete
   - Click **Open [filename] in Power BI**

2. **Verify in Browser:**
   - Opens Power BI Service (app.powerbi.com)
   - Your report is now in the cloud

#### Step 2: Configure Data Source Credentials

1. **In Power BI Service (browser):**
   - Go to **Workspaces** → **My workspace** (or your workspace)
   - Find your dataset (same name as your report)
   - Click **⋯** (three dots) next to dataset
   - Select **Settings**

2. **Data source credentials:**
   - Expand **Data source credentials**
   - You'll see your Google Sheets URL
   - Click **Edit credentials**
   - Authentication method: **Anonymous** (Google Sheets public link)
   - Privacy level: **Public**
   - Click **Sign in**

#### Step 3: Configure Scheduled Refresh

1. **Still in Settings:**
   - Scroll to **Scheduled refresh** section
   - Toggle **Keep your data up to date** to **ON**

2. **Refresh frequency:**
   - Select **Daily** or **Weekly**
   - For weekly: Choose **Monday** (day after your scraper runs)

3. **Time:**
   - Add time slot: **9:00 AM** (your timezone)
   - This gives scraper time to finish (runs Sunday 2 AM UTC)

4. **Time zone:**
   - Select your timezone
   - Example: **(UTC+01:00) Amsterdam, Berlin, Bern, Rome, Stockholm, Vienna**

5. **Email notifications:**
   - ✓ Send refresh failure notifications to me
   - Add email addresses if needed

6. **Click Apply**

#### Step 4: Test Refresh

1. **Manual test:**
   - In dataset settings
   - Click **Refresh now** at top
   - Wait 1-2 minutes
   - Check if data updated

2. **Verify:**
   - Open your report
   - Check product count
   - Verify latest data appears

#### Step 5: Monitor Refresh History

1. **View refresh history:**
   - Dataset settings
   - Scroll to **Refresh history**
   - See all past refreshes
   - Status: Success/Failed
   - Duration
   - Error messages (if any)

---

## Complete Automatic Workflow

### With Power BI Service (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│                    SUNDAY 2:00 AM UTC                       │
│                    Render runs scraper                      │
│                    ~20,000 products scraped                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    (75 minutes later)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    SUNDAY 3:15 AM UTC                       │
│                    Google Sheets updated                    │
│                    New data available                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    (Wait for Monday)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    MONDAY 9:00 AM                           │
│                    Power BI Service auto-refresh            │
│                    Pulls from Google Sheets                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    MONDAY 9:02 AM                           │
│                    Dashboard updated                        │
│                    Users see fresh data                     │
│                    Email notification sent (if enabled)     │
└─────────────────────────────────────────────────────────────┘
```

### Timeline
- **Sunday 2:00 AM UTC**: Scraper starts
- **Sunday 3:15 AM UTC**: Google Sheets updated
- **Monday 9:00 AM**: Power BI refreshes
- **Monday 9:02 AM**: Dashboard shows new data

---

## Power BI Service Configuration Details

### Refresh Frequency Options

#### Daily Refresh
```
Frequency: Daily
Time slots: Up to 8 per day (Pro) or 48 per day (Premium)
Example: 9:00 AM every day
```

**When to use:**
- If scraper runs daily
- Need fresh data every day

#### Weekly Refresh ⭐ RECOMMENDED
```
Frequency: Weekly
Days: Monday (day after scraper runs)
Time: 9:00 AM
```

**When to use:**
- Scraper runs weekly (Sunday)
- Data doesn't change daily
- Saves refresh quota

### Refresh Limits

#### Power BI Pro
- **Daily refreshes**: 8 per day
- **Weekly refreshes**: Unlimited
- **Dataset size**: Up to 1 GB
- **Cost**: $10/user/month

#### Power BI Premium
- **Daily refreshes**: 48 per day
- **Weekly refreshes**: Unlimited
- **Dataset size**: Up to 10 GB
- **Cost**: $20/user/month or $4,995/month (capacity)

### Your Use Case
- **Data size**: ~20,000 rows = ~5-10 MB ✓
- **Update frequency**: Weekly ✓
- **Recommendation**: Power BI Pro is sufficient

---

## Alternative: Power BI Gateway (For Private Data)

### When to Use
- If Google Sheets is private (not public)
- If data is on-premises
- If you need real-time data

### Setup (Brief)
1. Install Power BI Gateway on a computer
2. Configure gateway to access Google Sheets
3. Set up scheduled refresh through gateway

**Note:** Not needed for your use case (public Google Sheets)

---

## Troubleshooting

### Issue: "Refresh failed - Unable to connect"
**Solution:**
1. Check Google Sheets is public
2. Verify URL is correct
3. Test URL in browser
4. Re-enter credentials in Power BI Service

### Issue: "Refresh failed - Data source error"
**Solution:**
1. Check Google Sheets has data
2. Verify column names match
3. Check for special characters
4. Test manual refresh in Power BI Desktop

### Issue: "Refresh takes too long"
**Solution:**
1. Reduce data size (filter in Power Query)
2. Remove unnecessary columns
3. Upgrade to Power BI Premium

### Issue: "Refresh quota exceeded"
**Solution:**
1. Reduce refresh frequency
2. Use weekly instead of daily
3. Upgrade to Premium

---

## Recommended Setup for Your Project

### Configuration
```
Platform: Power BI Service (cloud)
License: Power BI Pro ($10/month)
Frequency: Weekly
Day: Monday
Time: 9:00 AM (your timezone)
Notifications: Enabled
```

### Why This Works
1. **Scraper runs**: Sunday 2 AM UTC
2. **Data ready**: Sunday 3:15 AM UTC
3. **Power BI refreshes**: Monday 9 AM (your timezone)
4. **Users see data**: Monday morning
5. **Fresh weekly data**: No manual work

### Cost Breakdown
```
Render.com: $0/month (free tier)
Google Sheets: $0/month (free)
Power BI Pro: $10/month (per user)
Total: $10/month per user
```

---

## Step-by-Step Quick Setup

### For Power BI Service (5 minutes)

1. **Publish report**
   - Power BI Desktop → Publish
   - Select workspace
   - Wait for upload

2. **Configure credentials**
   - Power BI Service → Dataset Settings
   - Edit credentials → Anonymous
   - Sign in

3. **Schedule refresh**
   - Scheduled refresh → ON
   - Weekly → Monday
   - Time → 9:00 AM
   - Apply

4. **Test**
   - Click "Refresh now"
   - Wait 2 minutes
   - Verify data updated

5. **Done!**
   - Automatic refresh every Monday
   - Email notifications enabled
   - Zero manual work

---

## Comparison: Desktop vs Service

| Feature | Power BI Desktop | Power BI Service |
|---------|------------------|------------------|
| **Cost** | Free | $10/month (Pro) |
| **Automatic** | No (needs Task Scheduler) | Yes (cloud-based) |
| **Computer needed** | Yes (must be on) | No |
| **Reliability** | Low | High |
| **Email alerts** | No | Yes |
| **Mobile access** | No | Yes |
| **Sharing** | Manual file sharing | Easy sharing |
| **Recommended** | For testing | For production ⭐ |

---

## Final Recommendation

### For Production Use: Power BI Service ⭐

**Setup:**
1. Get Power BI Pro license ($10/month)
2. Publish your dashboard to Power BI Service
3. Configure scheduled refresh (Weekly, Monday 9 AM)
4. Enable email notifications
5. Done!

**Benefits:**
- Truly automatic (no computer needed)
- Reliable cloud-based refresh
- Email notifications
- Mobile access
- Easy sharing with team
- Professional solution

**Total Cost:**
- Render: $0/month
- Google Sheets: $0/month
- Power BI Pro: $10/month per user
- **Total: $10/month** for complete automation

---

## Summary

✅ **Best Solution**: Power BI Service with scheduled refresh
✅ **Frequency**: Weekly (Monday 9 AM)
✅ **Cost**: $10/month per user
✅ **Setup Time**: 5 minutes
✅ **Maintenance**: Zero

Your complete automated pipeline:
1. **Sunday 2 AM**: Scraper runs on Render
2. **Sunday 3 AM**: Google Sheets updated
3. **Monday 9 AM**: Power BI auto-refreshes
4. **Monday 9 AM**: Users see fresh data

**No manual work required!** 🎉
