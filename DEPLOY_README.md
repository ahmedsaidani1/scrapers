# 🚀 Deploy to Render - Power BI Production

## Quick Deploy (5 Minutes)

### 1️⃣ Create Render Account
Go to: https://render.com/

### 2️⃣ Create Cron Job
```
New + → Cron Job
Connect GitHub repo
```

### 3️⃣ Configure
```
Name: powerbi-scraper-production
Build: pip install -r requirements.txt
Command: python run_production_powerbi.py
Schedule: 0 2 * * 0
```

### 4️⃣ Add Credentials
```
Environment Variables:
Key: GOOGLE_APPLICATION_CREDENTIALS
Value: [Paste entire credentials.json content]
```

### 5️⃣ Deploy & Test
```
Click "Create Cron Job"
Click "Trigger Run"
Watch logs for success
```

## 📊 What Happens

Every Sunday at 2 AM UTC:
- Scrapes ALL products from 9 websites
- ~20,000 products total
- Pushes to Google Sheet automatically
- Power BI auto-refreshes
- Done! ✓

## 📚 Documentation

- **Quick Start**: `PRODUCTION_QUICK_START.md` (5 min read)
- **Full Guide**: `RENDER_DEPLOYMENT_GUIDE.md` (15 min read)
- **Checklist**: `DEPLOYMENT_CHECKLIST.md` (step-by-step)
- **Architecture**: `PRODUCTION_ARCHITECTURE.md` (system design)
- **Summary**: `DEPLOYMENT_SUMMARY.md` (overview)

## 💰 Cost

**FREE** - $0/month on free tier

## ✅ Success

You're done when:
- Render cron job running
- Google Sheets updating
- Power BI refreshing
- Zero manual work

## 🆘 Need Help?

Read: `PRODUCTION_QUICK_START.md`

---

**Start here**: `PRODUCTION_QUICK_START.md` → Deploy in 5 minutes! 🚀
