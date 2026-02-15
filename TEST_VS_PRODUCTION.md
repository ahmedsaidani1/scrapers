# Test vs Production - Power BI Pipeline

## Overview

You have TWO scripts for different purposes:

## 🧪 TEST Script: `run_power_bi_test.py`

### Purpose
Quick testing and validation

### Configuration
```python
# Limits products per scraper
product_count = scraper.run(max_products=2000)
```

### Output
- ~18,000 products (2000 × 9 scrapers)
- Fast execution (~30-60 minutes)
- Same Google Sheet ID

### When to Use
- Testing changes locally
- Validating scrapers work
- Quick data samples
- Development

### Run Locally
```bash
python run_power_bi_test.py
```

---

## 🚀 PRODUCTION Script: `run_production_powerbi.py`

### Purpose
Full production data pipeline

### Configuration
```python
# NO LIMITS - scrape everything
product_count = scraper.run(max_products=None)
```

### Output
- ~20,000-25,000 products (ALL products from all sites)
- Longer execution (~60-120 minutes)
- Same Google Sheet ID

### When to Use
- Production deployment on Render
- Weekly automated runs
- Full data collection
- Real business use

### Run on Render
Automatically every Sunday at 2 AM UTC

---

## Key Differences

| Feature | Test | Production |
|---------|------|------------|
| **Products per scraper** | 2,000 limit | ALL (no limit) |
| **Total products** | ~18,000 | ~20,000-25,000 |
| **Execution time** | 30-60 min | 60-120 min |
| **Where it runs** | Local machine | Render.com |
| **Schedule** | Manual | Automatic (weekly) |
| **Purpose** | Testing | Production data |
| **Google Sheet** | Same | Same |
| **Shopify** | Not included | Not included |

---

## Data Flow (Both Scripts)

```
Scrapers → CSV Files → Google Sheet → Power BI
```

Both scripts:
- Use same 9 scrapers
- Push to same Google Sheet
- Convert prices to numbers
- Add source column
- Work with Power BI

---

## Which One to Deploy?

### Deploy to Render: `run_production_powerbi.py` ✅
- Full data collection
- Automatic scheduling
- Production-ready
- No limits

### Keep Local: `run_power_bi_test.py` ✅
- Quick testing
- Development
- Validation
- Faster feedback

---

## Migration Path

### Current State
You have `run_power_bi_test.py` working locally

### Next Step
Deploy `run_production_powerbi.py` to Render

### Result
- Local: Use test script for development
- Production: Render runs production script weekly
- Both push to same Google Sheet
- Power BI always has latest data

---

## Files for Render Deployment

Only these files are needed on Render:

```
run_production_powerbi.py  ← Main script
render.yaml                ← Render config
Procfile                   ← Process config
runtime.txt                ← Python version
requirements.txt           ← Dependencies
credentials/credentials.json ← Google auth (as env var)
+ All scraper files
+ config.py
+ google_sheets_helper.py
```

---

## Summary

- **Test locally** with `run_power_bi_test.py` (2000 products/scraper)
- **Deploy to Render** with `run_production_powerbi.py` (ALL products)
- Both use same infrastructure
- Both push to same Google Sheet
- Power BI works with both
- Production gives you complete data automatically

---

**Ready to deploy?** See `PRODUCTION_QUICK_START.md`
