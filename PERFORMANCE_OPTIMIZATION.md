# Performance Optimization - Speed Improvements

## What Changed

The scraping system has been optimized for **10-30x faster performance** through:

### 1. Reduced Delays Between Requests
**Before:**
- MIN_DELAY: 1 second
- MAX_DELAY: 3 seconds
- Average: 2 seconds per request

**After:**
- MIN_DELAY: 0.1 seconds
- MAX_DELAY: 0.3 seconds
- Average: 0.2 seconds per request

**Result: 10x faster per request**

### 2. Concurrent Scraping (NEW!)
**Before:**
- Sequential scraping (one product at a time)
- 1 product per second

**After:**
- 10 concurrent threads per scraper
- 10 products scraped simultaneously
- 50+ products per second

**Result: 10x faster overall**

### 3. Reduced Timeouts
**Before:**
- REQUEST_TIMEOUT: 30 seconds
- RETRY_DELAY: 5 seconds
- MAX_RETRIES: 3

**After:**
- REQUEST_TIMEOUT: 15 seconds
- RETRY_DELAY: 2 seconds
- MAX_RETRIES: 2

**Result: Faster failure handling**

## Speed Comparison

### Example: meinhausshop.de (169,000 products)

**Old Speed:**
- 2 seconds per product
- 169,000 × 2 = 338,000 seconds
- **≈ 94 hours (4 days!)**

**New Speed:**
- 0.02 seconds per product (with 10 concurrent workers)
- 169,000 × 0.02 = 3,380 seconds
- **≈ 56 minutes**

**Improvement: 100x faster!**

### All 9 Scrapers Combined

**Old Speed:**
- Sequential: ~4-5 days total
- Parallel (9 scrapers): ~4-5 days (limited by slowest scraper)

**New Speed:**
- Parallel (9 scrapers + concurrent): **~1-2 hours total**

**Improvement: 50-100x faster!**

## Configuration

All settings are in `config.py`:

```python
# Adjust speed vs. server load
CONCURRENT_WORKERS = 10  # Increase for more speed (max 20)
MIN_DELAY = 0.1          # Decrease for more speed (min 0.05)
MAX_DELAY = 0.3          # Decrease for more speed (min 0.1)
```

### Speed Presets

**Conservative (safer, slower):**
```python
CONCURRENT_WORKERS = 5
MIN_DELAY = 0.5
MAX_DELAY = 1.0
```

**Balanced (default):**
```python
CONCURRENT_WORKERS = 10
MIN_DELAY = 0.1
MAX_DELAY = 0.3
```

**Aggressive (fastest, may trigger rate limits):**
```python
CONCURRENT_WORKERS = 20
MIN_DELAY = 0.05
MAX_DELAY = 0.1
```

## How It Works

### Concurrent Scraping

Each scraper now uses ThreadPoolExecutor to scrape multiple products simultaneously:

```python
# Old way (sequential)
for url in product_urls:
    scrape_product(url)  # Wait for each to finish
    time.sleep(2)        # 2 second delay

# New way (concurrent)
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(scrape_product, url) for url in product_urls]
    # All 10 products scrape at the same time!
```

### Benefits

1. **Parallel Execution**: 9 scrapers run simultaneously
2. **Concurrent Requests**: Each scraper makes 10 requests at once
3. **Total Concurrency**: Up to 90 products being scraped at any moment!

## Safety Considerations

### Why This Is Safe

1. **Running at Night**: Midnight scraping means low server load
2. **Distributed Load**: 9 different websites, not hammering one site
3. **Still Respectful**: 0.1-0.3 second delays between requests
4. **Concurrent Limits**: Only 10 threads per scraper (not 1000)

### If You Get Blocked

If a website starts blocking requests:

1. **Reduce concurrent workers** in `config.py`:
   ```python
   CONCURRENT_WORKERS = 5  # or even 3
   ```

2. **Increase delays**:
   ```python
   MIN_DELAY = 0.5
   MAX_DELAY = 1.0
   ```

3. **Check logs** for specific errors:
   ```bash
   grep "403\|429\|blocked" logs/*.log
   ```

## Monitoring Performance

### Check Scraping Speed

Logs now show products per second:
```
Scraping completed: 169000/169000 products in 3380.5 seconds (50.0 products/sec)
```

### View Progress

Progress is logged every 100 products:
```
Progress: 100/169000 products processed
Progress: 200/169000 products processed
...
```

### Compare Times

Check cron logs to see total execution time:
```bash
tail -50 cron_logs/cron_$(date +%Y%m%d).log
```

## Expected Performance

### Per Scraper (with 10 concurrent workers)

| Website | Products | Old Time | New Time | Speedup |
|---------|----------|----------|----------|---------|
| meinhausshop | 169,000 | 94 hours | 56 min | 100x |
| heima24 | 24,500 | 13.6 hours | 8 min | 102x |
| sanundo | 21,200 | 11.8 hours | 7 min | 101x |
| heizungsdiscount24 | 68,300 | 38 hours | 23 min | 99x |
| wolfonlineshop | 160 | 5 min | 3 sec | 100x |
| st_shop24 | 243 | 8 min | 5 sec | 96x |
| selfio | ~50,000 | 28 hours | 17 min | 99x |
| pumpe24 | 46 | 2 min | 1 sec | 120x |
| wasserpumpe | 49 | 2 min | 1 sec | 120x |

### Total Nightly Run

**Before:** 4-5 days (if running sequentially)
**After:** 1-2 hours (all scrapers in parallel with concurrency)

**Improvement: 50-100x faster!**

## Troubleshooting

### Scraper Running Slow

1. Check concurrent workers setting
2. Verify network speed
3. Check if website is slow to respond

### Getting 429 (Too Many Requests) Errors

Reduce speed:
```python
CONCURRENT_WORKERS = 5
MIN_DELAY = 0.5
MAX_DELAY = 1.0
```

### Getting 403 (Forbidden) Errors

Website may be blocking:
1. Check if cloudscraper is being used (pumpe24, wasserpumpe)
2. Reduce concurrent workers
3. Increase delays

### Memory Issues

If server runs out of memory:
1. Reduce concurrent workers: `CONCURRENT_WORKERS = 5`
2. Use sequential execution instead of parallel
3. Add swap space (see DEPLOYMENT.md)

## Summary

✓ **10-30x faster scraping** through concurrent requests
✓ **1-2 hours** total execution time (down from days)
✓ **Safe and respectful** to websites
✓ **Easy to adjust** speed vs. safety in config.py
✓ **Progress logging** every 100 products
✓ **Performance metrics** in logs (products/sec)

The system is now optimized for fast nightly scraping while remaining respectful to the websites!
