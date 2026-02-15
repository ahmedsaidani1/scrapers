# Power BI Auto-Refresh - Quick Guide

## 🚀 5-Minute Setup

### What You Need
- Power BI Pro license ($10/month)
- Your Power BI dashboard file (.pbix)
- Google Sheets URL (already configured)

---

## Step 1: Publish to Cloud (2 minutes)

### In Power BI Desktop:
1. Open your dashboard
2. Click **Home** → **Publish**
3. Sign in with Microsoft account
4. Select **My workspace**
5. Click **Select**
6. Wait for "Success!"
7. Click **Open in Power BI**

✅ Your dashboard is now in the cloud!

---

## Step 2: Configure Data Source (1 minute)

### In Power BI Service (browser):
1. Go to **Workspaces** → **My workspace**
2. Find your dataset (same name as report)
3. Click **⋯** (three dots)
4. Select **Settings**
5. Expand **Data source credentials**
6. Click **Edit credentials**
7. Select **Anonymous**
8. Privacy: **Public**
9. Click **Sign in**

✅ Power BI can now access Google Sheets!

---

## Step 3: Schedule Refresh (2 minutes)

### Still in Settings:
1. Scroll to **Scheduled refresh**
2. Toggle **Keep your data up to date** → **ON**
3. Refresh frequency: **Weekly**
4. Day: **Monday** ✓
5. Time: **9:00 AM** ✓
6. Time zone: Select yours
7. Email notifications: ✓ **ON**
8. Click **Apply**

✅ Automatic refresh configured!

---

## Step 4: Test (1 minute)

### Test immediately:
1. At top of settings page
2. Click **Refresh now**
3. Wait 1-2 minutes
4. Go to your report
5. Verify data updated

✅ Working perfectly!

---

## 📅 Your Automatic Schedule

```
┌─────────────────────────────────────────┐
│  SUNDAY 2:00 AM UTC                     │
│  Render scrapes websites                │
│  ~20,000 products collected             │
└─────────────────────────────────────────┘
              ↓ (75 min)
┌─────────────────────────────────────────┐
│  SUNDAY 3:15 AM UTC                     │
│  Google Sheets updated                  │
│  Fresh data available                   │
└─────────────────────────────────────────┘
              ↓ (Wait for Monday)
┌─────────────────────────────────────────┐
│  MONDAY 9:00 AM                         │
│  Power BI auto-refreshes                │
│  Pulls from Google Sheets               │
└─────────────────────────────────────────┘
              ↓ (2 min)
┌─────────────────────────────────────────┐
│  MONDAY 9:02 AM                         │
│  Dashboard shows fresh data             │
│  Email notification sent ✓              │
│  Users can view updated dashboard       │
└─────────────────────────────────────────┘
```

---

## ✅ What's Automated

- ✅ Weekly scraping (Sunday 2 AM)
- ✅ Google Sheets update (automatic)
- ✅ Power BI refresh (Monday 9 AM)
- ✅ Email notifications (on success/failure)
- ✅ Mobile access (Power BI app)
- ✅ Team sharing (easy)

---

## 💰 Cost

```
Render.com:      $0/month  (free tier)
Google Sheets:   $0/month  (free)
Power BI Pro:    $10/month (per user)
─────────────────────────────────────
Total:           $10/month per user
```

---

## 🔍 Monitor Refresh

### View Refresh History:
1. Dataset Settings
2. Scroll to **Refresh history**
3. See all past refreshes:
   - ✓ Success
   - ✗ Failed
   - Duration
   - Error messages

### Email Notifications:
- Receive email if refresh fails
- No email if successful (optional)
- Configure in Settings

---

## 🚨 Troubleshooting

### Refresh Failed?

**Check:**
1. Google Sheets is public
2. URL is correct
3. Data source credentials set
4. Internet connection OK

**Fix:**
1. Re-enter credentials (Anonymous)
2. Test URL in browser
3. Click "Refresh now" again

---

## 📱 Access Your Dashboard

### Desktop:
- Power BI Desktop (edit)
- Power BI Service (view)

### Web:
- https://app.powerbi.com
- Sign in
- View/share reports

### Mobile:
- Download Power BI app
- Sign in
- View on phone/tablet

---

## 👥 Share with Team

### Share Dashboard:
1. Open report in Power BI Service
2. Click **Share** button
3. Enter email addresses
4. Set permissions:
   - ✓ Allow recipients to share
   - ✓ Allow recipients to build content
5. Click **Share**

### Team Access:
- They receive email with link
- Click to view dashboard
- Auto-refreshes for everyone
- No manual updates needed

---

## 🎯 Summary

**Setup Time:** 5 minutes
**Cost:** $10/month per user
**Maintenance:** Zero
**Reliability:** High (cloud-based)

**Your complete workflow:**
1. Scraper runs automatically (Sunday)
2. Google Sheets updates automatically
3. Power BI refreshes automatically (Monday)
4. Users see fresh data automatically

**Everything is automated!** 🎉

---

## 📞 Need Help?

### Full Guide:
Read: `POWER_BI_AUTO_REFRESH_SETUP.md`

### Power BI Support:
- https://powerbi.microsoft.com/support/

### Quick Questions:
- Check refresh history in Power BI Service
- Test with "Refresh now" button
- Verify Google Sheets has data

---

**You're all set!** Your Power BI dashboard will automatically refresh every Monday with fresh data from your scrapers. 🚀
