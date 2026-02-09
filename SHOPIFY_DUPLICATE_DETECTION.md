# Shopify Duplicate Detection & Price Updates

## ✅ Feature Implemented

The Shopify integration now includes **automatic duplicate detection** and **price update functionality**.

---

## 🔍 How It Works

### **Step 1: Check for Existing Product**
When syncing a product, the script:
1. Extracts the SKU from CSV data
2. Searches Shopify for existing product with that SKU
3. If found → Compares prices
4. If not found → Creates new product

### **Step 2: Three Possible Outcomes**

#### **A) Product Doesn't Exist → CREATE**
```
CSV: GRUNDFOS Pump (SKU: ABC123, Price: €2,615.05)
Shopify: No product with SKU ABC123

Action: ✓ Created new product
Result: Product created as DRAFT
```

#### **B) Product Exists, Same Price → SKIP**
```
CSV: GRUNDFOS Pump (SKU: ABC123, Price: €2,615.05)
Shopify: GRUNDFOS Pump (SKU: ABC123, Price: €2,615.05)

Action: ⊙ Unchanged (skipped)
Result: No changes made
```

#### **C) Product Exists, Different Price → UPDATE**
```
CSV: GRUNDFOS Pump (SKU: ABC123, Price: €2,750.00)
Shopify: GRUNDFOS Pump (SKU: ABC123, Price: €2,615.05)

Action: ✓ Updated (€2,615.05 → €2,750.00)
Result: Price updated in Shopify
```

---

## 📊 Real-World Scenarios

### **Scenario 1: First Run (Fresh Start)**
```
Sunday 5:00 AM - First sync
├── 31,488 products in CSV
├── 0 products in Shopify
└── Result: ✓ Created 31,488 products
```

### **Scenario 2: Second Run (Same Day)**
```
Sunday 6:00 AM - Accidental second run
├── 31,488 products in CSV
├── 31,488 products in Shopify (from first run)
└── Result: ⊙ Unchanged 31,488 (all skipped - no duplicates!)
```

### **Scenario 3: Weekly Run (No Price Changes)**
```
Next Sunday 5:00 AM - Weekly sync
├── 31,488 products in CSV (same prices)
├── 31,488 products in Shopify
└── Result: ⊙ Unchanged 31,488 (all skipped)
```

### **Scenario 4: Weekly Run (Some Prices Changed)**
```
Next Sunday 5:00 AM - Weekly sync
├── 31,488 products in CSV
│   ├── 30,000 same prices
│   └── 1,488 price changes
├── 31,488 products in Shopify
└── Result:
    ├── ⊙ Unchanged: 30,000
    ├── ✓ Updated: 1,488 (prices updated)
    └── ✓ Created: 0
```

### **Scenario 5: New Products Added**
```
Next Sunday 5:00 AM - Weekly sync
├── 32,000 products in CSV (512 new products)
├── 31,488 products in Shopify
└── Result:
    ├── ⊙ Unchanged: 31,488 (existing)
    └── ✓ Created: 512 (new products)
```

---

## 🎯 Benefits

### **No More Duplicates**
- ✓ Run script multiple times safely
- ✓ No manual cleanup needed
- ✓ Clean Shopify product list

### **Automatic Price Updates**
- ✓ Prices stay current
- ✓ No manual price editing
- ✓ Reflects latest competitor prices

### **Efficient Syncing**
- ✓ Only updates what changed
- ✓ Skips unchanged products
- ✓ Faster execution

### **Safe to Automate**
- ✓ Can run weekly without issues
- ✓ Won't create duplicates
- ✓ Won't overwrite manual edits (for published products)

---

## 📝 Output Examples

### **First Run:**
```
======================================================================
Syncing: heima24.csv
======================================================================
[1/5] Mehrschichtverbundrohr 16 x 2 mm...
  → Price being sent: 403.67
  ✓ Created: Mehrschichtverbundrohr 16 x 2 mm
[2/5] Mehrschichtverbundrohr 20 x 2 mm...
  → Price being sent: 79.62
  ✓ Created: Mehrschichtverbundrohr 20 x 2 mm

✓ Created: 2, Updated: 0, Unchanged: 0, Failed: 0
```

### **Second Run (No Changes):**
```
======================================================================
Syncing: heima24.csv
======================================================================
[1/5] Mehrschichtverbundrohr 16 x 2 mm...
  ⊙ Unchanged: Mehrschichtverbundrohr 16 x 2 mm (€403.67)
[2/5] Mehrschichtverbundrohr 20 x 2 mm...
  ⊙ Unchanged: Mehrschichtverbundrohr 20 x 2 mm (€79.62)

✓ Created: 0, Updated: 0, Unchanged: 2, Failed: 0
```

### **Third Run (Price Changed):**
```
======================================================================
Syncing: heima24.csv
======================================================================
[1/5] Mehrschichtverbundrohr 16 x 2 mm...
  ✓ Updated: Mehrschichtverbundrohr 16 x 2 mm (€403.67 → €420.00)
[2/5] Mehrschichtverbundrohr 20 x 2 mm...
  ⊙ Unchanged: Mehrschichtverbundrohr 20 x 2 mm (€79.62)

✓ Created: 0, Updated: 1, Unchanged: 1, Failed: 0
```

---

## ⚙️ Technical Details

### **Duplicate Detection Method**
- **Primary Key:** SKU (article_number)
- **Fallback:** If no SKU, product is always created (no duplicate check)
- **Search:** GraphQL query to Shopify API
- **Comparison:** Exact price match (string comparison)

### **What Gets Updated**
Currently only **price** is updated. Other fields (title, description, images) are NOT updated to preserve manual edits.

### **What Doesn't Get Updated**
- ✗ Product title
- ✗ Description
- ✗ Images
- ✗ SKU
- ✗ Barcode
- ✗ Vendor
- ✗ Product type
- ✗ Tags

**Why?** To preserve any manual edits you make in Shopify admin.

### **Performance**
- **Extra API calls:** 1 search query per product (before create/update)
- **Rate limiting:** 0.6 seconds delay per product
- **Total time:** ~5-6 hours for 31,488 products

---

## 🚨 Important Notes

### **Products Without SKU**
If a product has no SKU in the CSV:
- ✗ Cannot detect duplicates
- ✓ Will create new product every time
- ⚠️ May result in duplicates

**Solution:** Ensure all products have SKUs in CSV files.

### **Manual Edits in Shopify**
If you manually edit a product in Shopify:
- ✓ Price will be overwritten on next sync (if different in CSV)
- ✓ Other fields (title, description) are preserved
- ✓ Published status is preserved

### **DRAFT vs ACTIVE Products**
- ✓ DRAFT products: Price updated automatically
- ✓ ACTIVE products: Price updated automatically
- ⚠️ Both are treated the same

---

## 📈 Statistics Tracking

Each sync shows:
- **Created:** New products added
- **Updated:** Existing products with price changes
- **Unchanged:** Existing products with same price (skipped)
- **Failed:** Products that couldn't be created/updated

Example:
```
TOTAL: Created 512, Updated 1,488, Unchanged 29,488, Failed 0
```

---

## ✅ Summary

**Before (No Duplicate Detection):**
- ✗ Creates duplicates every run
- ✗ Manual cleanup required
- ✗ Messy product list

**After (With Duplicate Detection):**
- ✓ No duplicates created
- ✓ Prices stay updated
- ✓ Clean product list
- ✓ Safe to run multiple times
- ✓ Fully automated

---

**Status:** READY FOR PRODUCTION
**Last Updated:** February 3, 2026
