# Deployment Checklist - Quick Reference

## ✅ Pre-Deployment Status

- [x] 10 scrapers ready
- [x] Production script complete
- [x] All dependencies in requirements.txt
- [x] Render config files created
- [x] Documentation complete

---

## 🚀 Deployment Steps (5 Minutes)

### Step 1: Push to GitHub (1 min)
```bash
git add .
git commit -m "Production ready: 10 scrapers"
git push origin main
```

### Step 2: Create Render Service (2 min)
1. Go to https://dashboard.render.com
2. Click "New +" → "Cron Job"
3. Connect GitHub repo
4. Fill in:
   - **Name**: `powerbi-scraper-production`
   - **Schedule**: `0 2 * * 0`
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `python run_production_powerbi.py`
5. Click "Create Cron Job"

### Step 3: Add Credentials (1 min)
1. In Render service → "Environment"
2. Add variable:
   - **Key**: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
   - **Value**: Paste entire `credentials/credentials.json` content
3. Click "Save Changes"

### Step 4: Test Deploy (1 min)
1. Click "Manual Deploy" button
2. Select "Deploy latest commit"
3. Watch logs - should see all 10 scrapers run

---

## 📊 What to Expect

### During Deploy
```
[MEMORY] Initial: ~50 MB
Running sanundo...
Running heima24...
Running st_shop24...
Running selfio...
Running heizungsdiscount24...
Running meinhausshop...
Running wolfonlineshop...
Running pumpe24...
Running pumpenheizung...
Running wasserpumpe...
[MEMORY] Final: ~400 MB
✓ Successfully pushed X products to Google Sheets
```

### After Deploy
- Check Google Sheet: https://docs.google.com/spreadsheets/d/1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg
- Should see 20,000-50,000+ products
- Data includes all 10 sources

---

## 🔧 Troubleshooting

### Issue: Out of Memory
**Solution**: Upgrade to Standard (2GB RAM)
- Render Dashboard → Service → "Upgrade"
- Cost: $0.20/month

### Issue: Scraper Timeout
**Solution**: Increase timeout in render.yaml
```yaml
startCommand: timeout 7200 python run_production_powerbi.py
```

### Issue: Google Sheets Error
**Solution**: Check credentials
- Verify `GOOGLE_APPLICATION_CREDENTIALS_JSON` is set
- Ensure credentials.json is valid
- Check Sheet ID is correct

---

## 📅 Schedule

### Automatic Runs
- **Every Sunday at 2:00 AM UTC**
- No manual intervention needed
- Data automatically pushed to Google Sheets

### Manual Runs
- Click "Manual Deploy" anytime
- Useful for testing or immediate updates

---

## 🎯 Success Criteria

✅ All 10 scrapers complete without errors
✅ Data appears in Google Sheet
✅ Memory usage stays under 512MB (or 2GB if upgraded)
✅ Total execution time under 2 hours
✅ Power BI can refresh from Google Sheet

---

## 📞 Quick Commands

### Check Logs
```bash
# In Render dashboard
Click "Logs" tab → View real-time output
```

### Manual Deploy
```bash
# In Render dashboard
Click "Manual Deploy" → "Deploy latest commit"
```

### View Data
```bash
# Google Sheet
https://docs.google.com/spreadsheets/d/1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg
```

---

## 🎉 You're Done!

Once deployed:
1. ✅ Scrapers run automatically every Sunday
2. ✅ Data pushed to Google Sheets
3. ✅ Power BI auto-refreshes Monday
4. ✅ Dashboard always up-to-date

**No more manual work needed!**

---

**Estimated Time**: 5 minutes
**Difficulty**: Easy
**Cost**: $0-10.20/month
