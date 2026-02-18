# MeinHausShop Scraper Debug Summary

## Issue
The meinhausshop scraper instances on Render are failing with "no products scraped, pipeline failed".

## Investigation

### Local Testing Results
✅ The scraper works perfectly locally:
- Part 1: 49,991 products
- Part 2: 49,972 products  
- Part 3: (not tested but should work)
- Part 4: (not tested but should work)

### Sitemap Structure
- Main sitemap: `https://meinhausshop.de/sitemap.xml`
- Contains 4 sub-sitemaps (gzipped):
  1. `https://www.meinhausshop.de/web/sitemap/shop-1/sitemap-1.xml.gz`
  2. `https://www.meinhausshop.de/web/sitemap/shop-1/sitemap-2.xml.gz`
  3. `https://www.meinhausshop.de/web/sitemap/shop-1/sitemap-3.xml.gz`
  4. `https://www.meinhausshop.de/web/sitemap/shop-1/sitemap-4.xml.gz`

### Render Configuration
The scraper is split into 4 instances in `render.yaml`:
- `powerbi-meinhausshop-p1`: `MEINHAUSSHOP_SITEMAP_PARTS=1` → worksheet `meinhausshop_p1`
- `powerbi-meinhausshop-p2`: `MEINHAUSSHOP_SITEMAP_PARTS=2` → worksheet `meinhausshop_p2`
- `powerbi-meinhausshop-p3`: `MEINHAUSSHOP_SITEMAP_PARTS=3` → worksheet `meinhausshop_p3`
- `powerbi-meinhausshop-p4`: `MEINHAUSSHOP_SITEMAP_PARTS=4` → worksheet `meinhausshop_p4`

## Changes Made

### Enhanced Logging
Added comprehensive logging to `meinhausshop_scraper.py` to diagnose Render issues:

1. **Environment Variable Logging**
   - Logs the raw value of `MEINHAUSSHOP_SITEMAP_PARTS`
   - Logs which parts are selected
   - Warns if invalid values are provided

2. **Sitemap Fetch Logging**
   - Logs HTTP status code for main sitemap
   - Logs number of `<loc>` tags found
   - Shows first 500 chars if no tags found

3. **Sitemap Processing Logging**
   - Logs which sitemaps are being skipped
   - Logs size of compressed sitemap (bytes)
   - Logs size of decompressed sitemap (bytes)
   - Logs number of URLs found in each sitemap
   - Logs number of product URLs extracted
   - Full stack traces for any errors

### Code Logic
The filtering logic is correct:
```python
for i, loc in enumerate(sitemap_locs, 1):  # 1-based indexing
    if selected_parts and i not in selected_parts:
        continue  # Skip if not in selected parts
    # Process this sitemap
```

## Next Steps

### When Deployed to Render
The enhanced logging will show exactly what's happening:

**If the main sitemap fetch fails:**
```
[ERROR] Failed to fetch main sitemap - make_request returned None
```

**If no sitemaps are found:**
```
[ERROR] No <loc> tags found in sitemap. Response length: XXX
[ERROR] First 500 chars of response: ...
```

**If environment variable is wrong:**
```
[INFO] MEINHAUSSHOP_SITEMAP_PARTS env var: ''
[INFO] No sitemap parts filter configured
```

**If gzip decompression fails:**
```
[ERROR] Failed to decompress sitemap X: ...
```

### Possible Render-Specific Issues

1. **Network/Firewall**: Render might be blocking access to meinhausshop.de
2. **Timeout**: The sitemap fetch might be timing out (though unlikely with current settings)
3. **Memory**: Decompressing large sitemaps might hit memory limits (though 7GB should be enough)
4. **SSL/TLS**: Certificate validation might be failing
5. **Rate Limiting**: The site might be rate-limiting Render's IP addresses

### Testing on Render
After deployment, check the logs for:
1. The exact value of `MEINHAUSSHOP_SITEMAP_PARTS`
2. Whether the main sitemap fetch succeeds
3. Whether sub-sitemaps are found
4. Whether gzip decompression works
5. How many URLs are extracted

## Files Modified
- `meinhausshop_scraper.py` - Enhanced logging throughout `get_product_urls()` and `_get_selected_sitemap_parts()`

## Files Created
- `debug_meinhausshop_parts.py` - Local testing script to verify sitemap parts filtering
