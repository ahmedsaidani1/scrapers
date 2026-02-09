# 🚀 Power BI Quick Reference - Article Number Search

## For Your Client: How to Search Products & Compare Prices

---

## ⚡ Quick Start (2 Minutes)

### 1. Open Power BI
- Launch **Power BI Desktop** on your computer
- Or go to **app.powerbi.com** (if published online)

### 2. Go to Article Search Page
- Click the **"Article Search"** tab at the bottom

### 3. Search for a Product
- **Option A:** Enter article number in search box
- **Option B:** Type product name in name search box

### 4. See Results Instantly
- ✅ All shops that have this product
- ✅ Price at each shop
- ✅ Cheapest shop highlighted in **GREEN**
- ✅ How much you **SAVE**

---

## 📊 What You See

```
┌─────────────────────────────────────────────┐
│ Search by Article Number: [12345____]       │
├─────────────────────────────────────────────┤
│ ✓ Cheapest Shop: meinhausshop               │
│ Best Price: €245.00                         │
│ You Save: €35.00 (12.5%)                    │
├─────────────────────────────────────────────┤
│ Price Comparison:                           │
│ meinhausshop    €245.00 ← CHEAPEST         │
│ heima24         €260.00                     │
│ sanundo         €269.00                     │
│ heizungsdis...  €272.00                     │
│ selfio          €280.00 ← MOST EXPENSIVE   │
└─────────────────────────────────────────────┘
```

---

## 🎯 Common Tasks

### Find Cheapest Price for Product

1. Enter article number
2. Look for **GREEN** highlighted price
3. Click **"View Product"** link
4. Buy from that shop!

### Compare Multiple Products

1. Search first product → Note cheapest shop
2. Clear search (click X)
3. Search second product → Note cheapest shop
4. Repeat for all products

### Export Price Comparison

1. Click **"..."** on price table
2. Select **"Export data"**
3. Choose **"Excel"**
4. Save file
5. Share with team!

### See Price Visually

- Look at the **bar chart**
- Shorter bar = cheaper price
- Longer bar = more expensive

### Check How Many Shops Have It

- Look at **"Shops Selling"** number
- More shops = more competition = better prices

---

## 🔍 Search Tips

### By Article Number

✅ **Works best when:**
- You have exact article number
- Product has unique identifier
- Comparing same product across shops

**Example:** `12345`, `ABC-789`, `SKU-456`

### By Product Name

✅ **Works best when:**
- You don't have article number
- Searching by brand/model
- Looking for similar products

**Example:** `Heating Valve`, `Grundfos Pump`, `Honeywell`

### Partial Search

- Type part of name: `Valve` finds all valves
- Type brand: `Grundfos` finds all Grundfos products
- Type category: `Pump` finds all pumps

---

## 💡 Understanding the Results

### Price Table Columns

| Column | What It Means |
|--------|---------------|
| **Shop** | Which website has the product |
| **Net Price** | Price without tax (for businesses) |
| **Gross Price** | Price with tax (final price) |
| **Link** | Click to go to product page |

### Color Coding

- 🟢 **Green** = Cheapest price (BUY HERE!)
- 🔴 **Red** = Most expensive (avoid)
- ⚪ **White** = Middle range

### Savings Calculation

```
You Save = Most Expensive - Cheapest
Example: €280 - €245 = €35 saved!
```

---

## 🔄 Data Updates

### When is data updated?

- **Every night at 2:00 AM**
- After scrapers run at midnight
- Automatic - no action needed

### How to refresh manually?

**Power BI Desktop:**
- Click **"Refresh"** button (top ribbon)
- Wait 1-2 minutes

**Power BI Service (online):**
- Data refreshes automatically
- Or click **"Refresh now"** in dataset settings

### Last updated time?

- Look at **"Last Updated"** card
- Shows: "Today 02:00" or similar

---

## 📱 Mobile Use

### On Phone/Tablet:

1. Download **Power BI Mobile** app
2. Sign in with your account
3. Open the dashboard
4. Use search boxes (optimized for mobile)
5. Swipe to see all shops

### Mobile Tips:

- Use portrait mode for best view
- Tap cards to see details
- Pinch to zoom on charts
- Swipe left/right between pages

---

## 🆘 Troubleshooting

### "No results found"

**Possible reasons:**
- Article number doesn't exist
- Typo in search
- Product not in any shop

**Solutions:**
- Check article number spelling
- Try searching by product name
- Try partial search

### "Only 1 shop shown"

**This means:**
- Only one shop has this product
- Other shops don't stock it
- No price comparison possible

**What to do:**
- Buy from that shop
- Or search for similar products

### "Prices seem old"

**Check:**
- Last updated time
- If it's before today, click Refresh
- If still old, contact admin

### "Can't click product link"

**Solutions:**
- Right-click → Open in new tab
- Copy link and paste in browser
- Check internet connection

---

## 📊 Advanced Features

### Filter by Price Range

1. Click price slicer (if available)
2. Drag slider to set min/max
3. See only products in that range

### Filter by Category

1. Click category dropdown
2. Select category (e.g., "Valves")
3. See only products in that category

### Filter by Manufacturer

1. Click manufacturer dropdown
2. Select brand (e.g., "Grundfos")
3. See only products from that brand

### Sort Results

- Click column header to sort
- Click again to reverse order
- Example: Sort by price (low to high)

---

## 💾 Saving Your Work

### Bookmark a Search

1. Search for product
2. **View** → **Bookmarks** → **Add**
3. Name it (e.g., "Valve XYZ")
4. Click bookmark to return anytime

### Export to Excel

1. Click **"..."** on any table
2. **Export data** → **Excel**
3. Choose location
4. Open in Excel

### Take Screenshot

1. **Windows:** Press `Win + Shift + S`
2. **Mac:** Press `Cmd + Shift + 4`
3. Select area
4. Paste in email/document

---

## 🎯 Best Practices

### For Purchasing Decisions:

1. ✅ Always search by article number (most accurate)
2. ✅ Check at least 3 shops
3. ✅ Consider shipping costs (not in dashboard)
4. ✅ Check product availability (click link)
5. ✅ Verify product specifications match

### For Price Monitoring:

1. ✅ Bookmark frequently purchased products
2. ✅ Check prices weekly
3. ✅ Export comparisons for records
4. ✅ Note seasonal price changes
5. ✅ Set up alerts (if available)

### For Team Collaboration:

1. ✅ Share dashboard link with team
2. ✅ Export comparisons to Excel
3. ✅ Add notes in Excel file
4. ✅ Create purchasing guidelines
5. ✅ Track savings over time

---

## 📞 Quick Help

### Common Questions:

**Q: How many products can I search?**
A: All 333,000+ products from 10 shops

**Q: Can I search multiple products at once?**
A: No, one at a time. Use Excel export for bulk.

**Q: Are prices guaranteed?**
A: Prices are from last scrape (nightly). Always verify on shop website.

**Q: Can I buy directly from dashboard?**
A: No, click "View Product" link to go to shop website.

**Q: What if prices differ on website?**
A: Prices may have changed. Dashboard shows last night's prices.

---

## 🔗 Related Documents

- **Full Setup Guide:** `POWER_BI_ARTICLE_SEARCH_GUIDE.md`
- **Step-by-Step Tutorial:** `POWER_BI_STEP_BY_STEP.md`
- **General Power BI Guide:** `POWER_BI_SETUP.md`
- **Integration Guide:** `POWER_BI_INTEGRATION.md`

---

## ✅ Quick Checklist

Before using dashboard:

- [ ] Power BI Desktop installed (or access to online version)
- [ ] Dashboard opened
- [ ] On "Article Search" page
- [ ] Search boxes visible
- [ ] Data is up-to-date (check "Last Updated")

When searching:

- [ ] Enter article number or product name
- [ ] Results appear in table
- [ ] Cheapest price highlighted in green
- [ ] Savings amount shown
- [ ] Product links work

---

## 🎉 You're Ready!

**Start searching for products and finding the best prices!**

Remember:
- 🟢 Green = Cheapest (buy here!)
- Search by article number for best results
- Data updates every night at 2 AM
- Export to Excel for records

**Happy price hunting!** 💰

