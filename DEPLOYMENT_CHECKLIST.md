# Deployment Checklist - Power BI Production

## Pre-Deployment

### ✅ Files Created
- [x] `run_production_powerbi.py` - Production script (no limits)
- [x] `render.yaml` - Render configuration
- [x] `Procfile` - Process definition
- [x] `runtime.txt` - Python 3.11
- [x] `requirements.txt` - All dependencies
- [x] `RENDER_DEPLOYMENT_GUIDE.md` - Full guide
- [x] `PRODUCTION_QUICK_START.md` - Quick reference
- [x] `TEST_VS_PRODUCTION.md` - Comparison

### ✅ Verify Locally
- [ ] Test script works: `python run_power_bi_test.py`
- [ ] Google Sheets push works
- [ ] All 9 scrapers functional
- [ ] Credentials file exists: `credentials/credentials.json`

### ✅ Prepare Repository
- [ ] Push all files to GitHub
- [ ] Verify `.gitignore` excludes sensitive files
- [ ] Ensure `credentials.json` is NOT in repo (will use env var)

---

## Render Deployment

### Step 1: Create Account
- [ ] Sign up at https://render.com/
- [ ] Verify email
- [ ] Connect GitHub account

### Step 2: Create Cron Job
- [ ] Click "New +" → "Cron Job"
- [ ] Select your repository
- [ ] Name: `powerbi-scraper-production`
- [ ] Environment: Python 3

### Step 3: Configure Build
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python run_production_powerbi.py`
- [ ] Schedule: `0 2 * * 0` (Sunday 2 AM UTC)

### Step 4: Environment Variables
- [ ] Add `GOOGLE_APPLICATION_CREDENTIALS`
- [ ] Paste entire `credentials/credentials.json` content
- [ ] Save

### Step 5: Deploy
- [ ] Click "Create Cron Job"
- [ ] Wait for initial build
- [ ] Check build logs for errors

---

## Testing

### Manual Test Run
- [ ] Click "Trigger Run" in Render dashboard
- [ ] Monitor logs in real-time
- [ ] Verify all 9 scrapers run
- [ ] Check for "Successfully pushed to Google Sheets"

### Verify Data Flow
- [ ] Open Google Sheet: `1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg`
- [ ] Verify new data appears
- [ ] Check product count (15k-25k expected)
- [ ] Verify source column exists
- [ ] Check prices are numbers (not text)

### Power BI Check
- [ ] Open Power BI Desktop
- [ ] Refresh data source
- [ ] Verify new products appear
- [ ] Check dashboard updates correctly

---

## Post-Deployment

### Configure Monitoring
- [ ] Set up email notifications in Render
- [ ] Add success/failure alerts
- [ ] Configure log retention

### Schedule Verification
- [ ] Confirm schedule: Every Sunday 2 AM UTC
- [ ] Convert to your timezone
- [ ] Adjust if needed

### Documentation
- [ ] Share `PRODUCTION_QUICK_START.md` with team
- [ ] Document Google Sheet ID
- [ ] Note Render dashboard URL

---

## Weekly Monitoring

### Every Monday (After Sunday Run)
- [ ] Check Render logs for success
- [ ] Verify Google Sheet updated
- [ ] Confirm Power BI has fresh data
- [ ] Review product counts

### Monthly Review
- [ ] Check scraper performance
- [ ] Review execution times
- [ ] Monitor costs (should be $0 on free tier)
- [ ] Update scrapers if websites changed

---

## Troubleshooting

### If Build Fails
1. Check requirements.txt has all dependencies
2. Verify Python version (3.11)
3. Check build logs for specific errors

### If Scrapers Fail
1. Check individual scraper logs
2. Verify websites haven't changed
3. Test locally first
4. Update scraper if needed

### If Google Sheets Push Fails
1. Verify credentials environment variable
2. Check service account permissions
3. Confirm sheet ID is correct
4. Test authentication locally

### If Timeout Occurs
1. Free tier: 90 minutes max
2. Consider upgrading to paid tier
3. Or split into multiple jobs

---

## Success Criteria

### ✅ Deployment Successful When:
- [ ] Render cron job created
- [ ] Manual test run completes
- [ ] All 9 scrapers successful
- [ ] 15k-25k products scraped
- [ ] Data pushed to Google Sheets
- [ ] Power BI refreshes correctly
- [ ] Schedule confirmed (Sunday 2 AM)
- [ ] No errors in logs

---

## Rollback Plan

### If Production Fails:
1. Keep using local `run_power_bi_test.py`
2. Run manually on your machine
3. Fix issues on Render
4. Re-deploy when ready

### Emergency Manual Run:
```bash
# On your local machine
python run_production_powerbi.py
```

---

## Support Resources

### Documentation
- `RENDER_DEPLOYMENT_GUIDE.md` - Full deployment guide
- `PRODUCTION_QUICK_START.md` - Quick reference
- `TEST_VS_PRODUCTION.md` - Script comparison

### External Links
- Render Docs: https://render.com/docs/cronjobs
- Cron Schedule: https://crontab.guru/
- Google Sheets API: https://developers.google.com/sheets

---

## Final Notes

### What's Automated
✅ Scraping all products (no limits)
✅ Pushing to Google Sheets
✅ Weekly schedule (Sunday 2 AM)
✅ Power BI auto-refresh

### What's NOT Included
❌ Shopify integration (removed as requested)
❌ Email notifications (can add later)
❌ Manual CSV exports (not needed)

### Cost
- **Free Tier**: $0/month (sufficient)
- **Paid Tier**: $7/month (if needed)

---

**Ready to deploy!** Follow `PRODUCTION_QUICK_START.md` for step-by-step instructions.
