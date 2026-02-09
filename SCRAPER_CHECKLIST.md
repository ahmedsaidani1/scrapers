# Scraper Development Checklist

Use this checklist for each of your 10 scrapers to ensure quality and consistency.

## Pre-Development

- [ ] Website URL identified
- [ ] Robots.txt checked (respect rules)
- [ ] Sample product pages reviewed
- [ ] Data structure understood
- [ ] Google Sheet created and ID obtained
- [ ] Service account has access to sheet

## Development Phase

### 1. Setup (5 minutes)

- [ ] Copy template: `cp scraper_template.py [name]_scraper.py`
- [ ] Update `SCRAPER_NAME` constant
- [ ] Add to `config.py` SCRAPER_CONFIGS
- [ ] Add to `config.py` SHEET_IDS

### 2. Implement get_product_urls() (15-30 minutes)

- [ ] Choose approach (sitemap, category pages, or API)
- [ ] Implement URL collection logic
- [ ] Test URL extraction independently
- [ ] Verify URLs are valid product pages
- [ ] Handle pagination if needed
- [ ] Add error handling
- [ ] Log progress

**Test command:**
```python
python3 -c "
from [name]_scraper import [Name]Scraper
scraper = [Name]Scraper()
urls = scraper.get_product_urls()
print(f'Found {len(urls)} URLs')
print('First 5:', urls[:5])
"
```

### 3. Implement scrape_product() (30-60 minutes)

#### Product Name
- [ ] CSS selector identified
- [ ] Extraction working
- [ ] Handles missing data
- [ ] Text cleaned (strip whitespace)

#### SKU
- [ ] CSS selector identified
- [ ] Extraction working
- [ ] Handles missing SKU
- [ ] Format standardized

#### Category
- [ ] CSS selector identified
- [ ] Extraction working
- [ ] Handles missing category
- [ ] Consistent naming

#### Price
- [ ] CSS selector identified
- [ ] Extraction working
- [ ] Currency symbols removed
- [ ] Format standardized (e.g., "1234.56")
- [ ] Handles sale prices vs regular prices

#### Availability
- [ ] CSS selector identified
- [ ] Extraction working
- [ ] Standardized values ("In Stock", "Out of Stock", etc.)
- [ ] Default value set if missing

#### Description
- [ ] CSS selector identified
- [ ] Extraction working
- [ ] HTML tags removed
- [ ] Length limited (500 chars recommended)
- [ ] Special characters handled

#### Product Image
- [ ] CSS selector identified
- [ ] Extraction working
- [ ] Absolute URL (not relative)
- [ ] Handles multiple image formats
- [ ] Handles lazy-loaded images

#### Product URL
- [ ] URL passed through correctly
- [ ] Absolute URL format

### 4. Testing (15-30 minutes)

#### Local Testing
- [ ] Run scraper: `python3 [name]_scraper.py`
- [ ] Check CSV output: `cat data/[name]_scraper.csv`
- [ ] Verify all columns present
- [ ] Check data quality
- [ ] Review logs: `cat logs/[name]_scraper.log`
- [ ] No errors in logs
- [ ] Success rate acceptable (>90%)

#### Google Sheets Testing
- [ ] Run with push: `python3 [name]_scraper.py --push-to-sheets`
- [ ] Open Google Sheet in browser
- [ ] Verify data uploaded correctly
- [ ] Check all columns populated
- [ ] Verify formatting

#### Edge Cases
- [ ] Test with missing images
- [ ] Test with missing SKU
- [ ] Test with out-of-stock products
- [ ] Test with special characters in names
- [ ] Test with very long descriptions

### 5. Code Quality (10 minutes)

- [ ] Code follows template structure
- [ ] CSS selectors documented with comments
- [ ] Error handling in place
- [ ] Logging statements added
- [ ] No hardcoded values
- [ ] Type hints used
- [ ] Docstrings present

### 6. Documentation (5 minutes)

- [ ] Add comments explaining selectors
- [ ] Document any special handling
- [ ] Note any website quirks
- [ ] Add example product URL in comments

## Deployment Phase

### 1. Pre-Deployment

- [ ] All local tests passing
- [ ] Google Sheets integration working
- [ ] Logs reviewed for issues
- [ ] Data quality verified

### 2. Server Upload

- [ ] Upload scraper file to server
- [ ] Upload updated config.py
- [ ] Upload updated run_all_scrapers.sh

```bash
scp [name]_scraper.py root@45.32.157.30:/root/solar-scrapers/
scp config.py root@45.32.157.30:/root/solar-scrapers/
scp run_all_scrapers.sh root@45.32.157.30:/root/solar-scrapers/
```

### 3. Server Testing

- [ ] SSH into server
- [ ] Navigate to project directory
- [ ] Test scraper: `python3 [name]_scraper.py`
- [ ] Check output files
- [ ] Test Google Sheets push
- [ ] Review logs

### 4. Integration

- [ ] Add to run_all_scrapers.sh
- [ ] Test batch execution
- [ ] Verify in master log

## Post-Deployment

### First Week Monitoring

- [ ] Day 1: Check logs and data
- [ ] Day 2: Verify cron execution
- [ ] Day 3: Check data quality
- [ ] Day 7: Review success rate

### Ongoing Maintenance

- [ ] Weekly log review
- [ ] Monthly data quality check
- [ ] Update selectors if website changes
- [ ] Monitor for errors

## Common Issues Checklist

### No Products Found
- [ ] Check get_product_urls() logic
- [ ] Verify sitemap/category URL
- [ ] Check CSS selectors
- [ ] Review website structure

### Missing Data Fields
- [ ] Verify CSS selectors in browser DevTools
- [ ] Check for dynamic content (JavaScript)
- [ ] Add fallback selectors
- [ ] Set default values

### Google Sheets Fails
- [ ] Verify sheet ID in config.py
- [ ] Check service account has access
- [ ] Verify credentials.json present
- [ ] Check network connectivity

### Getting Blocked
- [ ] Increase delays (MIN_DELAY, MAX_DELAY)
- [ ] Add more user agents
- [ ] Check robots.txt compliance
- [ ] Reduce request frequency

### Scraper Crashes
- [ ] Review error logs
- [ ] Add try/except blocks
- [ ] Handle None values
- [ ] Validate data before saving

## Quality Standards

### Data Quality
- [ ] >90% of products have all fields
- [ ] Prices are numeric and valid
- [ ] Images are valid URLs
- [ ] Descriptions are readable
- [ ] No HTML tags in text fields

### Performance
- [ ] Scrapes at reasonable speed (2-3 sec/product)
- [ ] Doesn't overload target website
- [ ] Handles errors gracefully
- [ ] Completes within reasonable time

### Code Quality
- [ ] Follows template structure
- [ ] Well commented
- [ ] No code duplication
- [ ] Error handling present
- [ ] Logging comprehensive

## Final Verification

Before marking scraper as "complete":

- [ ] Runs successfully 3 times in a row
- [ ] Data quality >90%
- [ ] Google Sheets updating correctly
- [ ] No errors in logs
- [ ] Integrated into batch script
- [ ] Tested on server
- [ ] Documentation complete

## Scraper Status Tracker

Use this to track your 10 scrapers:

| # | Website | Status | CSV | Sheets | Deployed | Notes |
|---|---------|--------|-----|--------|----------|-------|
| 1 | | ⬜ Not Started | ⬜ | ⬜ | ⬜ | |
| 2 | | ⬜ Not Started | ⬜ | ⬜ | ⬜ | |
| 3 | | ⬜ Not Started | ⬜ | ⬜ | ⬜ | |
| 4 | | ⬜ Not Started | ⬜ | ⬜ | ⬜ | |
| 5 | | ⬜ Not Started | ⬜ | ⬜ | ⬜ | |
| 6 | | ⬜ Not Started | ⬜ | ⬜ | ⬜ | |
| 7 | | ⬜ Not Started | ⬜ | ⬜ | ⬜ | |
| 8 | | ⬜ Not Started | ⬜ | ⬜ | ⬜ | |
| 9 | | ⬜ Not Started | ⬜ | ⬜ | ⬜ | |
| 10 | | ⬜ Not Started | ⬜ | ⬜ | ⬜ | |

Status Legend:
- ⬜ Not Started
- 🟡 In Progress
- ✅ Complete
- ❌ Issues

## Time Estimates

Per scraper:
- Setup: 5 minutes
- get_product_urls(): 15-30 minutes
- scrape_product(): 30-60 minutes
- Testing: 15-30 minutes
- Deployment: 10 minutes
- **Total: 1.5-2.5 hours per scraper**

For 10 scrapers:
- **Total development time: 15-25 hours**
- Spread over 3-5 days recommended

## Tips for Efficiency

1. **Do similar websites together** - Reuse selector patterns
2. **Test frequently** - Don't wait until the end
3. **Use browser DevTools** - Find selectors quickly
4. **Copy working code** - Reuse patterns that work
5. **Start simple** - Get basic version working first
6. **Document as you go** - Don't wait until the end

## Success Metrics

A scraper is successful when:
- ✅ Runs without errors
- ✅ Extracts >90% of products
- ✅ All required fields populated
- ✅ Data quality is high
- ✅ Google Sheets updating
- ✅ Integrated into batch script
- ✅ Running on schedule

Good luck building your scrapers! 🚀
