# Render Deployment Guide - Power BI Production Pipeline

## Overview
This guide will help you deploy the Power BI scraper to Render.com for automatic weekly execution.

## What This Does
- Scrapes ALL products from 9 websites (no limits)
- Pushes data to Google Sheet: `1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg`
- Power BI auto-refreshes from the Google Sheet
- Runs automatically every Sunday at 2 AM UTC
- NO Shopify integration (removed from production flow)

## Prerequisites
1. Render.com account (free tier works)
2. Google Cloud credentials JSON file
3. GitHub repository with your code

## Step 1: Prepare Your Repository

### 1.1 Files Already Created
✓ `run_production_powerbi.py` - Main production script
✓ `render.yaml` - Render configuration
✓ `Procfile` - Process configuration
✓ `runtime.txt` - Python version
✓ `requirements.txt` - Dependencies

### 1.2 Add Google Credentials
You need to add your `credentials/credentials.json` file as an environment variable on Render.

## Step 2: Deploy to Render

### 2.1 Create New Cron Job
1. Go to https://render.com/
2. Click "New +" → "Cron Job"
3. Connect your GitHub repository

### 2.2 Configure the Cron Job
- **Name**: `powerbi-scraper-production`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Command**: `python run_production_powerbi.py`
- **Schedule**: `0 2 * * 0` (Every Sunday at 2 AM UTC)

### 2.3 Add Environment Variables
Click "Environment" tab and add:

**GOOGLE_APPLICATION_CREDENTIALS**
- Copy the entire contents of your `credentials/credentials.json` file
- Paste it as the value
- This allows the script to authenticate with Google Sheets

### 2.4 Advanced Settings (Optional)
- **Region**: Choose closest to your target websites (Europe recommended)
- **Instance Type**: Free tier is sufficient
- **Auto-Deploy**: Enable (deploys automatically on git push)

## Step 3: Test the Deployment

### 3.1 Manual Test Run
1. Go to your Cron Job dashboard on Render
2. Click "Trigger Run" to test immediately
3. Watch the logs to ensure it runs successfully

### 3.2 Check the Output
1. Verify logs show all 9 scrapers running
2. Check Google Sheet has new data
3. Verify Power BI dashboard updates

## Step 4: Schedule Configuration

### Current Schedule
- **Frequency**: Weekly (every Sunday)
- **Time**: 2:00 AM UTC
- **Cron Expression**: `0 2 * * 0`

### Change Schedule (if needed)
Edit `render.yaml` and change the schedule line:

```yaml
schedule: "0 2 * * 0"  # Every Sunday at 2 AM UTC
```

Common schedules:
- Daily at 2 AM: `0 2 * * *`
- Every Monday at 3 AM: `0 3 * * 1`
- Twice a week (Mon & Thu): `0 2 * * 1,4`
- First day of month: `0 2 1 * *`

## Production Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    RENDER CRON JOB                          │
│              (Runs Every Sunday 2 AM UTC)                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              run_production_powerbi.py                      │
│                                                             │
│  1. MeinHausShop    → Scrape ALL products                  │
│  2. Heima24         → Scrape ALL products                  │
│  3. Sanundo         → Scrape ALL products                  │
│  4. Heizungsdiscount24 → Scrape ALL products               │
│  5. Wolfonlineshop  → Scrape ALL products                  │
│  6. StShop24        → Scrape ALL products                  │
│  7. Selfio          → Scrape ALL products                  │
│  8. Pumpe24         → Scrape ALL products                  │
│  9. Wasserpumpe     → Scrape ALL products                  │
│                                                             │
│  Expected: 15,000 - 25,000 total products                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   GOOGLE SHEETS                             │
│         Sheet ID: 1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu... │
│                                                             │
│  - All products combined                                    │
│  - Source column added                                      │
│  - Prices converted to numbers                              │
│  - Ready for Power BI                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      POWER BI                               │
│                                                             │
│  - Auto-refreshes from Google Sheet                        │
│  - No manual work needed                                    │
│  - Dashboard updates automatically                          │
└─────────────────────────────────────────────────────────────┘
```

## Monitoring & Logs

### View Logs
1. Go to Render dashboard
2. Click on your Cron Job
3. Click "Logs" tab
4. See real-time execution logs

### What to Look For
✓ All 9 scrapers complete successfully
✓ Total product count (15k-25k expected)
✓ "Successfully pushed to Google Sheets" message
✓ No error messages

### Email Notifications (Optional)
Render can send email notifications on:
- Job success
- Job failure
- Configure in Settings → Notifications

## Troubleshooting

### Issue: Google Sheets Authentication Failed
**Solution**: 
- Verify `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set correctly
- Ensure the service account has edit access to the sheet

### Issue: Scraper Timeout
**Solution**:
- Render free tier has 90-minute timeout
- If scrapers take longer, upgrade to paid tier
- Or split into multiple cron jobs

### Issue: Memory Limit
**Solution**:
- Free tier has 512MB RAM
- If exceeded, upgrade instance type
- Or process scrapers in batches

### Issue: Rate Limiting
**Solution**:
- Some websites may block Render IPs
- Add delays in scrapers
- Consider using proxy service

## Cost Estimate

### Free Tier (Recommended for Start)
- **Cost**: $0/month
- **Limits**: 
  - 90 minutes execution time
  - 512MB RAM
  - Sufficient for this use case

### Paid Tier (If Needed)
- **Starter**: $7/month
  - 400 minutes execution time
  - 1GB RAM
- **Standard**: $25/month
  - Unlimited execution time
  - 2GB RAM

## Maintenance

### Weekly Checks
1. Check Render logs for successful runs
2. Verify Google Sheet has fresh data
3. Confirm Power BI dashboard updated

### Monthly Tasks
1. Review scraper performance
2. Check for website changes
3. Update scrapers if needed

### Updates
When you update code:
1. Push to GitHub
2. Render auto-deploys (if enabled)
3. Next scheduled run uses new code

## Support

### Render Documentation
- https://render.com/docs/cronjobs

### Common Commands
```bash
# Test locally before deploying
python run_production_powerbi.py

# Check requirements
pip install -r requirements.txt

# View logs
# (Use Render dashboard)
```

## Success Checklist

- [ ] Render account created
- [ ] Repository connected
- [ ] Cron job configured
- [ ] Environment variables set
- [ ] Test run successful
- [ ] Google Sheet updated
- [ ] Power BI refreshed
- [ ] Schedule confirmed
- [ ] Monitoring set up

## Next Steps

1. Deploy to Render following steps above
2. Run manual test
3. Verify data flow
4. Set up monitoring
5. Let it run automatically!

---

**That's it!** Your production pipeline is now automated. Every Sunday, fresh data flows from websites → Google Sheets → Power BI automatically.
