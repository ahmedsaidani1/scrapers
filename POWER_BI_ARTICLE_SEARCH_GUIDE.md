# 🔍 Power BI: Search Products by Article Number & Compare Prices

## Client Requirement
> "Search products by article number in Power BI and find the products from the different shops and their prices"

This guide shows you exactly how to build a Power BI dashboard where you can:
1. **Search by article number** (or product name)
2. **See which shops have that product**
3. **Compare prices across all shops**
4. **Find the cheapest option instantly**

---

## 📊 What You'll Build

A dashboard with:
- **Search box** to enter article number
- **Product details** card showing the searched product
- **Price comparison table** showing all shops that have it
- **Visual price comparison** bar chart
- **Cheapest shop** highlighted automatically

---

## 🚀 Step-by-Step Setup

### STEP 1: Load All Your Data (If Not Done Already)

Follow the existing `POWER_BI_STEP_BY_STEP.md` guide to:
1. Load all 9 Google Sheets
2. Add "source" column to each
3. Combine into "All Products" table

**Result:** One table with ~333,000 products from all shops

---

### STEP 2: Create the Search Dashboard Page

#### 2.1 Create New Page

1. At the bottom of Power BI, click **"+"** to add new page
2. Rename it to **"Article Search"**

#### 2.2 Add Page Title

1. **Insert** → **Text box**
2. Type: `Product Search & Price Comparison`
3. Format:
   - Font size: **28**
   - Bold: **Yes**
   - Alignment: **Center**
4. Position at top of page

---

### STEP 3: Add Article Number Search

#### 3.1 Create Search Slicer

1. Click **Slicer** visualization
2. Drag **"article_number"** field to the slicer
3. With slicer selected, click **Format** (paint roller icon)
4. Expand **"Slicer settings"**
5. Turn **ON** the **"Search"** option
6. Style: **Dropdown**
7. Single select: **ON**

#### 3.2 Format the Search Box

1. Still in Format pane
2. Expand **"Slicer header"**
   - Title text: `Search by Article Number`
   - Font size: **14**
   - Font color: **Dark blue**
3. Expand **"Values"**
   - Font size: **12**
4. Position at top-left of canvas (below title)

#### 3.3 Add Alternative Search by Product Name

1. Add another **Slicer**
2. Drag **"name"** field to it
3. Format:
   - Search: **ON**
   - Style: **Dropdown**
   - Header: `Or Search by Product Name`
4. Position next to article number slicer

---

### STEP 4: Show Product Details

#### 4.1 Create Product Info Card

1. Click **Card** visualization
2. Drag **"name"** field to the card
3. Format:
   - Callout value font size: **18**
   - Category label: **ON**
   - Category label text: `Product Name`
4. Position below search boxes

#### 4.2 Add Manufacturer Card

1. Add another **Card**
2. Drag **"manufacturer"** to it
3. Format:
   - Category label: **ON**
   - Category label text: `Manufacturer`
4. Position next to product name card

#### 4.3 Add Category Card

1. Add another **Card**
2. Drag **"category"** to it
3. Format:
   - Category label: **ON**
   - Category label text: `Category`
4. Position next to manufacturer card

---

### STEP 5: Create Price Comparison Table

#### 5.1 Add Table Visual

1. Click **Table** visualization
2. Drag these fields (in order):
   - **source** (Shop name)
   - **price_net** (Net price)
   - **price_gross** (Gross price)
   - **product_url** (Link to product)
3. Position in center of canvas (make it wide)

#### 5.2 Format the Table

1. With table selected, click **Format**
2. Expand **"Column headers"**
   - Font size: **14**
   - Font color: **White**
   - Background color: **Dark blue**
3. Expand **"Values"**
   - Font size: **12**
   - Alternate row color: **ON**
4. Expand **"Grid"**
   - Vertical grid: **ON**
   - Horizontal grid: **ON**
5. Expand **"Title"**
   - Title: **ON**
   - Title text: `Price Comparison Across All Shops`
   - Font size: **16**

#### 5.3 Add Conditional Formatting (Highlight Cheapest)

1. Click on **price_gross** column in the table
2. Right-click → **Conditional formatting** → **Background color**
3. Format style: **Rules**
4. Rules:
   - If value **is lowest** → Color: **Light green**
5. Click **OK**

Now the cheapest price will be highlighted in green!

---

### STEP 6: Add Visual Price Comparison

#### 6.1 Create Bar Chart

1. Click **Clustered bar chart** visualization
2. Drag fields:
   - **Y-axis**: source (shop name)
   - **X-axis**: price_gross
3. Format:
   - Title: **ON**
   - Title text: `Price Comparison (Visual)`
   - Data labels: **ON**
   - Data labels position: **Outside end**
   - Data labels display units: **None**
   - Data labels value decimal places: **2**
4. Position below the price table

#### 6.2 Add Color Coding

1. With bar chart selected, click **Format**
2. Expand **"Data colors"**
3. Turn **ON** "Show all"
4. Assign different color to each shop:
   - meinhausshop: **Blue**
   - heima24: **Green**
   - sanundo: **Orange**
   - heizungsdiscount24: **Red**
   - wolfonlineshop: **Purple**
   - st_shop24: **Teal**
   - selfio: **Yellow**
   - pumpe24: **Pink**
   - wasserpumpe: **Brown**
   - glo24: **Gray**

---

### STEP 7: Add "Cheapest Shop" Indicator

#### 7.1 Create DAX Measure for Cheapest Price

1. Click **Home** → **New Measure**
2. In formula bar, type:
```dax
Cheapest Price = MIN('All Products'[price_gross])
```
3. Press **Enter**

#### 7.2 Create DAX Measure for Cheapest Shop

1. **Home** → **New Measure**
2. Formula:
```dax
Cheapest Shop = 
CALCULATE(
    SELECTEDVALUE('All Products'[source]),
    FILTER(
        'All Products',
        'All Products'[price_gross] = [Cheapest Price]
    )
)
```
3. Press **Enter**

#### 7.3 Display Cheapest Shop

1. Add **Card** visualization
2. Drag **"Cheapest Shop"** measure to it
3. Format:
   - Callout value font size: **24**
   - Callout value font color: **Green**
   - Category label: **ON**
   - Category label text: `✓ Cheapest Shop`
   - Category label font size: **16**
4. Position prominently (top-right corner)

#### 7.4 Display Cheapest Price

1. Add another **Card**
2. Drag **"Cheapest Price"** measure to it
3. Format:
   - Callout value font size: **28**
   - Callout value font color: **Green**
   - Category label: **ON**
   - Category label text: `Best Price`
   - Display units: **None**
   - Value decimal places: **2**
4. Position next to cheapest shop card

---

### STEP 8: Add Savings Calculator

#### 8.1 Create Maximum Price Measure

1. **Home** → **New Measure**
2. Formula:
```dax
Highest Price = MAX('All Products'[price_gross])
```

#### 8.2 Create Savings Measure

1. **Home** → **New Measure**
2. Formula:
```dax
Potential Savings = [Highest Price] - [Cheapest Price]
```

#### 8.3 Create Savings Percentage

1. **Home** → **New Measure**
2. Formula:
```dax
Savings % = 
DIVIDE(
    [Potential Savings],
    [Highest Price],
    0
) * 100
```

#### 8.4 Display Savings

1. Add **Card** visualization
2. Drag **"Potential Savings"** to it
3. Format:
   - Callout value font size: **24**
   - Callout value font color: **Red**
   - Category label: **ON**
   - Category label text: `You Save`
   - Display units: **None**
   - Value decimal places: **2**
4. Position below cheapest price card

5. Add another **Card** for percentage
6. Drag **"Savings %"** to it
7. Format similarly with **"%"** suffix

---

### STEP 9: Add Shop Count Indicator

#### 9.1 Create Shop Count Measure

1. **Home** → **New Measure**
2. Formula:
```dax
Shops Selling = DISTINCTCOUNT('All Products'[source])
```

#### 9.2 Display Shop Count

1. Add **Card** visualization
2. Drag **"Shops Selling"** to it
3. Format:
   - Callout value font size: **32**
   - Category label: **ON**
   - Category label text: `Shops Selling This Product`
4. Position at top of page

---

### STEP 10: Add Product Image (Optional)

If your data has product images:

1. Add **Image** visualization
2. Drag **"product_image"** field to it
3. Format:
   - Image fit: **Fit**
   - Title: **OFF**
4. Position on right side of page

---

## 📐 Final Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│              Product Search & Price Comparison                      │
├──────────────────────────┬──────────────────────────────────────────┤
│ Search by Article Number │ Or Search by Product Name               │
│ [Dropdown with search]   │ [Dropdown with search]                  │
├──────────────────────────┴──────────────────────────────────────────┤
│                                                                      │
│ Shops Selling: 5         ✓ Cheapest Shop    Best Price    You Save │
│                          meinhausshop        €245.00       €35.00   │
│                                                            (12.5%)   │
├──────────────────────────────────────────────────────────────────────┤
│ Product Name             Manufacturer        Category               │
│ Heating Valve XYZ        Honeywell          Valves                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ Price Comparison Across All Shops                                  │
│ ┌────────────────┬──────────┬────────────┬─────────────────────┐  │
│ │ Shop           │ Net      │ Gross      │ Link                │  │
│ ├────────────────┼──────────┼────────────┼─────────────────────┤  │
│ │ meinhausshop   │ €205.88  │ €245.00 ✓  │ [View Product]      │  │
│ │ heima24        │ €218.49  │ €260.00    │ [View Product]      │  │
│ │ sanundo        │ €226.05  │ €269.00    │ [View Product]      │  │
│ │ heizungsdis... │ €228.57  │ €272.00    │ [View Product]      │  │
│ │ selfio         │ €235.29  │ €280.00    │ [View Product]      │  │
│ └────────────────┴──────────┴────────────┴─────────────────────┘  │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ Price Comparison (Visual)                                           │
│ meinhausshop     ████████████████████ €245.00                      │
│ heima24          ██████████████████████ €260.00                    │
│ sanundo          ███████████████████████ €269.00                   │
│ heizungsdis...   ████████████████████████ €272.00                  │
│ selfio           █████████████████████████ €280.00                 │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 How to Use the Dashboard

### For Your Client:

1. **Open Power BI Desktop** (or Power BI Service if published)
2. **Go to "Article Search" page**
3. **Click the article number search box**
4. **Type or paste the article number** (e.g., "12345")
5. **Press Enter or select from dropdown**

**Instantly see:**
- ✅ Which shops have this product
- ✅ Price at each shop
- ✅ Cheapest shop highlighted in green
- ✅ How much you save by choosing cheapest
- ✅ Visual comparison bar chart
- ✅ Direct links to product pages

### Alternative Search Methods:

**By Product Name:**
- Use the "Search by Product Name" box
- Type part of the product name
- Select from filtered results

**By Browsing:**
- Go to "All Products" page (from your existing setup)
- Use category/manufacturer filters
- Click on a product
- Use drill-through to see price comparison

---

## 🔧 Advanced Features

### Feature 1: Price History (If You Keep Historical Data)

If you save snapshots weekly:

1. Create a **Date** table
2. Link to your products table
3. Add **Line chart**:
   - Axis: Date
   - Legend: source (shop)
   - Values: price_gross
4. Shows price trends over time

### Feature 2: Price Alert Threshold

Create a measure to highlight deals:

```dax
Is Good Deal = 
IF(
    'All Products'[price_gross] < [Average Price] * 0.9,
    "🔥 Great Deal!",
    ""
)
```

Add this to your table as a column.

### Feature 3: Similar Products

Show products in same category:

1. Add **Table** visualization
2. Filter by same category as selected product
3. Sort by price
4. Title: "Similar Products"

### Feature 4: Availability Indicator

```dax
Availability = 
"Available at " & [Shops Selling] & " shops"
```

### Feature 5: Price Range Indicator

```dax
Price Range = 
"€" & [Cheapest Price] & " - €" & [Highest Price]
```

---

## 📱 Mobile Version

For mobile users:

1. **View** → **Mobile Layout**
2. Drag essential visuals:
   - Search box
   - Product name
   - Cheapest shop card
   - Best price card
   - Price comparison table (simplified)
3. Remove:
   - Bar chart (too wide)
   - Extra cards
   - Images

---

## 🔄 Auto-Refresh Setup

### For Real-Time Price Updates:

1. **Publish to Power BI Service**
2. **Configure scheduled refresh**:
   - Frequency: **Daily**
   - Time: **2:00 AM** (after your scrapers run at midnight)
3. **Enable automatic page refresh** (Premium feature):
   - Refresh interval: **Every hour**
   - Keeps prices up-to-date during the day

---

## 🎨 Customization Tips

### Branding:

1. Add company logo (Insert → Image)
2. Use company colors for cards and charts
3. Add footer with contact info

### User Experience:

1. Add **"Clear Filters"** button
2. Add **"Reset"** bookmark
3. Add **"Help"** text box with instructions
4. Add **"Last Updated"** timestamp

### Performance:

1. Limit search results to top 100 matches
2. Use aggregated data where possible
3. Remove unused columns in Power Query
4. Enable query folding

---

## 🐛 Troubleshooting

### Problem: Search box shows too many results

**Solution:**
- In slicer settings, set "Show items with no data" to **OFF**
- Add a filter to show only products with article numbers

### Problem: Multiple products with same article number

**Solution:**
- This is expected (same product from different shops)
- The table shows all shops selling it
- Use DISTINCTCOUNT to count unique products

### Problem: Some shops don't appear

**Solution:**
- They don't have that specific product
- Check if article number is correct
- Verify data was scraped from that shop

### Problem: Prices not updating

**Solution:**
- Click **Refresh** button
- Check if scrapers ran successfully
- Verify Google Sheets have new data
- Check scheduled refresh settings

---

## ✅ Testing Checklist

Test your dashboard:

- [ ] Search by article number works
- [ ] Search by product name works
- [ ] Price table shows all shops
- [ ] Cheapest price is highlighted in green
- [ ] Bar chart displays correctly
- [ ] Cheapest shop card shows correct shop
- [ ] Savings calculation is accurate
- [ ] Product links work
- [ ] Filters can be cleared
- [ ] Mobile layout is usable
- [ ] Refresh updates data

---

## 📊 Sample Article Numbers to Test

Use these from your data:

1. Search for a common product (appears in multiple shops)
2. Search for a rare product (only 1-2 shops)
3. Search for expensive product (>€1000)
4. Search for cheap product (<€50)
5. Search by partial name

---

## 🎓 Training for Your Client

### Quick Start Guide for Client:

**To find best price for a product:**

1. Open Power BI dashboard
2. Click "Article Search" page
3. Enter article number in search box
4. See instant price comparison
5. Click "View Product" link for cheapest shop
6. Done!

**Tips:**
- Green = cheapest price
- Red = most expensive
- "You Save" shows savings vs highest price
- All prices updated daily at 2 AM

---

## 📞 Support

**For your client:**

**Common Questions:**

Q: How often are prices updated?
A: Daily at 2:00 AM (after midnight scraping)

Q: What if a product isn't found?
A: Try searching by product name instead, or check if article number is correct

Q: Can I export the comparison?
A: Yes! Click "..." on table → Export data → Excel

Q: Can I see price history?
A: Yes, if historical data is enabled (contact admin)

Q: How do I share this with my team?
A: Publish to Power BI Service and share the link

---

## 🚀 Next Steps

1. ✅ Build the article search page (Steps 1-10)
2. ✅ Test with sample article numbers
3. ✅ Customize colors and branding
4. ✅ Publish to Power BI Service
5. ✅ Set up auto-refresh
6. ✅ Train your client
7. ✅ Create mobile version
8. ✅ Add advanced features (optional)

---

## 💡 Pro Tips

1. **Bookmark common searches** - Save frequently searched products
2. **Create product categories page** - Browse by category first
3. **Add manufacturer filter** - Find all products from specific brand
4. **Use drill-through** - Click product to see detailed comparison
5. **Export to Excel** - Share comparisons with team
6. **Set up alerts** - Get notified when prices drop
7. **Create favorites list** - Track specific products
8. **Add notes field** - Let users add comments

---

## ✅ Summary

You now have a complete **Product Search & Price Comparison** dashboard that:

✅ Searches by article number or product name
✅ Shows which shops have the product
✅ Compares prices across all shops
✅ Highlights cheapest option in green
✅ Calculates potential savings
✅ Provides direct links to products
✅ Updates automatically every night
✅ Works on desktop and mobile

**Your client can now find the best price for any product in seconds!** 🎉

