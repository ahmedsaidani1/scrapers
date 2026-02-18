# MeinHausShop Scraper Timeout Fix

## Issue
The meinhausshop scraper instances on Render were failing because the main sitemap (`https://meinhausshop.de/sitemap.xml`) was timing out after 60 seconds (twice).

```
2026-02-18 21:14:51 - meinhausshop - WARNING - Timeout for https://meinhausshop.de/sitemap.xml (attempt 1/2)
2026-02-18 21:15:53 - meinhausshop - WARNING - Timeout for https://meinhausshop.de/sitemap.xml (attempt 2/2)
2026-02-18 21:15:53 - meinhausshop - ERROR - Failed to fetch https://meinhausshop.de/sitemap.xml after 2 attempts
```

## Root Cause
The website is either:
1. Blocking Render's IP addresses
2. Rate-limiting cloud providers
3. Having slow response times for certain regions
4. The main sitemap.xml is slower than the individual sitemap files

## Solution Implemented

### 1. Extended Timeout
- Increased timeout from 60s to 120s for sitemap requests
- Updated `base_scraper.py` to support custom timeout parameter in `make_request()`

### 2. Direct Sitemap Fallback
Added `_get_urls_from_direct_sitemaps()` method that bypasses the main sitemap index and fetches the known sitemap files directly:
- `https://www.meinhausshop.de/web/sitemap/shop-1/sitemap-1.xml.gz`
- `https://www.meinhausshop.de/web/sitemap/shop-1/sitemap-2.xml.gz`
- `https://www.meinhausshop.de/web/sitemap/shop-1/sitemap-3.xml.gz`
- `https://www.meinhausshop.de/web/sitemap/shop-1/sitemap-4.xml.gz`

### 3. Automatic Fallback Logic
The scraper now:
1. First tries to fetch the main sitemap with 120s timeout
2. If that fails, automatically switches to direct sitemap method
3. Still respects the `MEINHAUSSHOP_SITEMAP_PARTS` environment variable in both methods

## Testing Results

### Local Testing
✅ Fallback method works perfectly:
```
Direct sitemap 1 fetched, size: 773660 bytes
Direct sitemap 1 decompressed, size: 9335554 bytes
Found 49999 URLs in direct sitemap 1
Extracted 49991 unique product URLs from direct sitemap 1
```

### Expected Behavior on Render
When the main sitemap times out, the scraper will:
1. Log: "Failed to fetch main sitemap, trying direct sitemap URLs..."
2. Log: "Using direct sitemap fallback method"
3. Fetch the individual sitemap files directly (which should be faster)
4. Extract products normally

## Files Modified

### meinhausshop_scraper.py
- Added `timeout=120` parameter to sitemap requests
- Added `_get_urls_from_direct_sitemaps()` fallback method
- Added automatic fallback logic in `get_product_urls()`
- Enhanced logging throughout

### base_scraper.py
- Updated `make_request()` to support custom `timeout` parameter via kwargs
- Allows scrapers to override the default timeout when needed

## Advantages of This Approach

1. **Resilient**: If main sitemap fails, fallback kicks in automatically
2. **Faster**: Direct sitemap files may load faster than the index
3. **Transparent**: Still respects environment variable filtering
4. **No Breaking Changes**: Works exactly the same when main sitemap is accessible
5. **Better Logging**: Clear indication of which method is being used

## Next Steps

Deploy to Render and monitor the logs. You should see either:

**Success with main sitemap:**
```
Main sitemap fetched successfully, status code: 200
Found 4 sub-sitemaps
Processing sitemap 1/4: ...
```

**Success with fallback:**
```
Failed to fetch main sitemap, trying direct sitemap URLs...
Using direct sitemap fallback method
Trying direct sitemap 1/4: ...
Direct sitemap 1 fetched, size: 773660 bytes
```

Both methods will produce the same results (~50,000 products per part).
