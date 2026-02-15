# Production vs Test Configuration

## ✅ PRODUCTION (Unlimited Scraping)

### File: `run_production_powerbi.py`
```python
# Line 97 in run_production_powerbi.py
product_count = scraper.run(max_products=None)  # ✓ Scrapes ALL products
```

### What It Does
- Scrapes **ALL products** from all 10 websites
- No limits, no restrictions
- Runs automatically every Sunday at 2 AM UTC
- Expected: 20,000-50,000+ products

### When It Runs
- **Automatically**: Every Sunday via Render Cron Job
- **Manually**: Can trigger from Render dashboard anytime

---

## 🧪 TEST (Limited Scraping)

### File: `test_pumpenheizung.py`
```python
# Line 17 in test_pumpenheizung.py
count = scraper.run(max_products=10)  # Only 10 products for testing
```

### What It Does
- Scrapes only **10 products** for quick testing
- Used to verify scraper works correctly
- Runs locally on your machine
- Expected: 10 products

### When It Runs
- **Manually**: When you run `python test_pumpenheizung.py`
- **Purpose**: Testing only, not for production data

---

## Quick Comparison

| Aspect | Production | Test |
|--------|-----------|------|
| **File** | `run_production_powerbi.py` | `test_pumpenheizung.py` |
| **Products** | ALL (unlimited) | 10 only |
| **Parameter** | `max_products=None` | `max_products=10` |
| **Scrapers** | All 10 scrapers | 1 scraper |
| **Schedule** | Automatic (Sunday 2 AM) | Manual |
| **Location** | Render.com cloud | Local machine |
| **Purpose** | Production data | Testing |
| **Output** | 20,000-50,000+ products | 10 products |

---

## How to Verify

### Check Production Script
```bash
python verify_production_config.py
```

Expected output:
```
✓ Production mode: max_products=None (scrapes ALL products)
```

### Check Code Directly
```bash
# Windows
findstr "max_products=None" run_production_powerbi.py

# Linux/Mac
grep "max_products=None" run_production_powerbi.py
```

Expected output:
```
product_count = scraper.run(max_products=None)
```

---

## ✅ Confirmation

**Production script is correctly configured:**
- ✓ File: `run_production_powerbi.py`
- ✓ Setting: `max_products=None`
- ✓ Behavior: Scrapes ALL products
- ✓ Scrapers: 10 total
- ✓ Schedule: Every Sunday 2 AM UTC

**Test scripts are correctly configured:**
- ✓ File: `test_pumpenheizung.py`
- ✓ Setting: `max_products=10`
- ✓ Behavior: Scrapes 10 products only
- ✓ Purpose: Testing and verification

---

## 🚀 Ready for Deployment

The production configuration is **correct** and **verified**.

When you deploy to Render, it will:
1. Run `run_production_powerbi.py`
2. Scrape ALL products from 10 websites
3. Push 20,000-50,000+ products to Google Sheets
4. Repeat automatically every Sunday

**No changes needed - ready to deploy!**
