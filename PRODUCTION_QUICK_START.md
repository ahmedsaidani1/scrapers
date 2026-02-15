# Production Quick Start - Power BI Pipeline

## 🚀 What You Have Now

### Production Script
`run_production_powerbi.py` - Scrapes ALL products, pushes to Google Sheets

### Deployment Files
- `render.yaml` - Render configuration
- `Procfile` - Process definition
- `runtime.txt` - Python 3.11
- `requirements.txt` - Dependencies

## 📋 Deploy in 5 Minutes

### 1. Go to Render.com
```
https://render.com/
```

### 2. Create Cron Job
- New + → Cron Job
- Connect GitHub repo
- Name: `powerbi-scraper-production`

### 3. Configure
- **Build**: `pip install -r requirements.txt`
- **Command**: `python run_production_powerbi.py`
- **Schedule**: `0 2 * * 0` (Sunday 2 AM)

### 4. Add Credentials
Environment Variables → Add:
- **Key**: `GOOGLE_APPLICATION_CREDENTIALS`
- **Value**: Paste entire `credentials/credentials.json` content

### 5. Deploy & Test
- Click "Create Cron Job"
- Click "Trigger Run" to test
- Watch logs for success

## ✅ What Happens

```
Every Sunday 2 AM UTC:
  ↓
9 Scrapers Run (ALL products, no limits)
  ↓
~20,000 products scraped
  ↓
Push to Google Sheet: 1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg
  ↓
Power BI auto-refreshes
  ↓
Done! 🎉
```

## 🔍 Monitor

**Render Dashboard** → Your Cron Job → Logs

Look for:
- ✓ All 9 scrapers successful
- ✓ Total products: 15k-25k
- ✓ "Successfully pushed to Google Sheets"

## 🛠️ Change Schedule

Edit `render.yaml`:
```yaml
schedule: "0 2 * * 0"  # Current: Sunday 2 AM
```

Common options:
- Daily: `0 2 * * *`
- Monday & Thursday: `0 2 * * 1,4`
- First of month: `0 2 1 * *`

## 💰 Cost

**Free Tier**: $0/month (sufficient for this)
- 90 min execution time
- 512MB RAM

## 📞 Need Help?

See `RENDER_DEPLOYMENT_GUIDE.md` for detailed instructions.

---

**You're ready to deploy!** 🚀
