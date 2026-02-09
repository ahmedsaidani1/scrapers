# Power BI Integration Guide

Complete guide to connect your Google Sheets data to Power BI for price comparison dashboards and analytics.

---

## 📊 Your Google Sheets

All 9 scrapers push data to these Google Sheets every night at midnight:

| Website | Products | Sheet URL |
|---------|----------|-----------|
| **meinhausshop** | ~169,000 | [Open Sheet](https://docs.google.com/spreadsheets/d/1KaMWOGh9KEPvvxWQRKLu-fLr0-aSLdhn5IbdZ0XyvTQ) |
| **heima24** | ~24,500 | [Open Sheet](https://docs.google.com/spreadsheets/d/1nfHVN4RZM-tED-HtXUWV7bwtAWjctih7dJ2eOyTRj08) |
| **sanundo** | ~21,200 | [Open Sheet](https://docs.google.com/spreadsheets/d/1ygsm7nK3glzapTCoM0X7Hk3x1-xY3ieTqRCdXJN5Y8A) |
| **heizungsdiscount24** | ~68,300 | [Open Sheet](https://docs.google.com/spreadsheets/d/1dwls46f4xW7Td5XrV8ShvLdwsPJwQhPieH342BOEZ8o) |
| **wolfonlineshop** | ~160 | [Open Sheet](https://docs.google.com/spreadsheets/d/1IR3BAObUJf4cUxdX9OF1zka0YsOrP35c-n8F4xIl3a8) |
| **st_shop24** | ~243 | [Open Sheet](https://docs.google.com/spreadsheets/d/1inV05kOmYe53iq0ujyDafftzxZgqWVnBriRbD-BOd_k) |
| **selfio** | ~50,000 | [Open Sheet](https://docs.google.com/spreadsheets/d/19evdUWIJX9hLK46XYp5avvlW9KZhGayjnw6fkwn2CfE) |
| **pumpe24** | ~46 | [Open Sheet](https://docs.google.com/spreadsheets/d/1eKkepxz9FtDVQNaQmBmPfnTqTcFz7kai0dxJ0JCwuGU) |
| **wasserpumpe** | ~49 | [Open Sheet](https://docs.google.com/spreadsheets/d/1iGmt66Y4mKwC06aT0NhKzWZ8GfcCtgY0oPdYVSY4Jz4) |

**Total: ~333,000 products updated nightly**

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Download Power BI Desktop
- Free download: https://powerbi.microsoft.com/desktop/
- Windows only (Mac users: use Power BI Service web version)

### Step 2: Connect Your First Sheet

1. Open Power BI Desktop
2. Click **"Get Data"** → Search for **"Web"**
3. Click **"Connect"**
4. Choose **"Basic"** and paste this URL:
   ```
   https://docs.google.com/spreadsheets/d/1KaMWOGh9KEPvvxWQRKLu-fLr0-aSLdhn5IbdZ0XyvTQ/export?format=csv
   ```
5. Click **"OK"**
6. Preview the data → Click **"Load"**

### Step 3: Create Your First Visual

1. Click **"Table"** visualization
2. Drag these fields to the table:
   - manufacturer
   - name
   - price_gross
   - category
3. Done! You now have a sortable product table

---

## � Connect All 9 Sheets

### Method 1: Using CSV Export URLs (Recommended - Fastest)

Power BI can directly import Google Sheets as CSV. Use these URLs:

```
meinhausshop:
https://docs.google.com/spreadsheets/d/1KaMWOGh9KEPvvxWQRKLu-fLr0-aSLdhn5IbdZ0XyvTQ/export?format=csv

heima24:
https://docs.google.com/spreadsheets/d/1nfHVN4RZM-tED-HtXUWV7bwtAWjctih7dJ2eOyTRj08/export?format=csv

sanundo:
https://docs.google.com/spreadsheets/d/1ygsm7nK3glzapTCoM0X7Hk3x1-xY3ieTqRCdXJN5Y8A/export?format=csv

heizungsdiscount24:
https://docs.google.com/spreadsheets/d/1dwls46f4xW7Td5XrV8ShvLdwsPJwQhPieH342BOEZ8o/export?format=csv

wolfonlineshop:
https://docs.google.com/spreadsheets/d/1IR3BAObUJf4cUxdX9OF1zka0YsOrP35c-n8F4xIl3a8/export?format=csv

st_shop24:
https://docs.google.com/spreadsheets/d/1inV05kOmYe53iq0ujyDafftzxZgqWVnBriRbD-BOd_k/export?format=csv

selfio:
https://docs.google.com/spreadsheets/d/19evdUWIJX9hLK46XYp5avvlW9KZhGayjnw6fkwn2CfE/export?format=csv

pumpe24:
https://docs.google.com/spreadsheets/d/1eKkepxz9FtDVQNaQmBmPfnTqTcFz7kai0dxJ0JCwuGU/export?format=csv

wasserpumpe:
https://docs.google.com/spreadsheets/d/1iGmt66Y4mKwC06aT0NhKzWZ8GfcCtgY0oPdYVSY4Jz4/export?format=csv
```

**For each sheet:**
1. Get Data → Web → Basic
2. Paste the CSV export URL
3. Click OK → Load
4. Rename the query to the website name (e.g., "meinhausshop")

### Method 2: Using Google Sheets Connector

1. Get Data → Search "Google Sheets"
2. Sign in with your Google account
3. Paste the sheet URL (without /export?format=csv)
4. Select "Sheet1" → Load

**Note:** Method 1 (CSV) is faster and doesn't require Google sign-in.

---

## 🔗 Combine All Sheets Into One Dataset

After loading all 9 sheets, combine them:

### Step 1: Add Source Column to Each Sheet

For each query (meinhausshop, heima24, etc.):

1. **Home** → **Transform Data** (opens Power Query Editor)
2. Select the query (e.g., "meinhausshop")
3. **Add Column** → **Custom Column**
4. Column name: `source`
5. Formula: `"meinhausshop"` (use the actual website name)
6. Click **OK**

Repeat for all 9 queries with their respective names.

### Step 2: Append All Queries

1. Select the first query (meinhausshop)
2. **Home** → **Append Queries** → **Append Queries as New**
3. Select **"Three or more tables"**
4. Add all 9 queries to the right side
5. Click **OK**
6. Rename the new query to **"All Products"**
7. **Home** → **Close & Apply**

Now you have one unified dataset with all 333,000+ products!

---

## 🎨 Sample Dashboard Visualizations

### 1. Key Metrics (Cards)

**Total Products:**
- Visual: Card
- Field: name (Count)

**Average Price:**
- Visual: Card
- Field: price_gross (Average)
- Format: Currency (€)

**Total Suppliers:**
- Visual: Card
- Field: source (Count Distinct)

### 2. Price Comparison by Source (Bar Chart)

- Visual: Clustered Bar Chart
- Axis: source
- Values: price_gross (Average)
- Shows: Which supplier has lowest average prices

### 3. Products by Category (Pie Chart)

- Visual: Pie Chart
- Legend: category
- Values: name (Count)
- Shows: Product distribution across categories

### 4. Top 10 Cheapest Products (Table)

- Visual: Table
- Fields: name, manufacturer, price_gross, source, product_url
- Filters: Top 10 by price_gross (ascending)

### 5. Price Distribution (Histogram)

- Visual: Column Chart
- Axis: price_gross (create bins: 0-100, 100-500, 500-1000, etc.)
- Values: name (Count)
- Shows: How many products in each price range

### 6. Products by Manufacturer (Tree Map)

- Visual: Treemap
- Group: manufacturer
- Values: name (Count)
- Shows: Which manufacturers have most products

---

## 📊 Sample Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Heating & Plumbing Equipment Price Comparison Dashboard        │
├──────────────┬──────────────┬──────────────┬──────────────────┤
│ Total        │ Avg Price    │ Suppliers    │ Last Updated     │
│ Products     │              │              │                  │
│ 333,498      │ €245         │ 9            │ Today 00:30      │
├──────────────┴──────────────┴──────────────┴──────────────────┤
│                                                                 │
│  Average Price by Supplier (Bar Chart)                         │
│  ████████████████ meinhausshop - €198                          │
│  ██████████████████ heima24 - €267                             │
│  ███████████████ sanundo - €234                                │
│  ...                                                            │
│                                                                 │
├─────────────────────────────┬───────────────────────────────────┤
│                             │                                   │
│  Products by Category       │  Top 10 Cheapest Products        │
│  (Pie Chart)                │  (Table)                         │
│                             │  Name      | Price | Supplier    │
│  ● Heating 45%              │  Valve     | €12   | sanundo    │
│  ● Plumbing 30%             │  Fitting   | €15   | heima24    │
│  ● Pumps 15%                │  ...                             │
│  ● Other 10%                │                                   │
│                             │                                   │
├─────────────────────────────┴───────────────────────────────────┤
│                                                                 │
│  All Products (Searchable Table with Filters)                  │
│  Name          | Manufacturer | Price | Category | Supplier   │
│  Heating Pump  | Grundfos     | €450  | Pumps    | pumpe24   │
│  Valve Set     | Honeywell    | €89   | Heating  | sanundo   │
│  ...                                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Auto-Refresh Setup

### Power BI Desktop (Manual Refresh)
- Click **"Refresh"** button anytime to get latest data
- Data updates from Google Sheets in real-time

### Power BI Service (Automatic Refresh)

1. **Publish to Power BI Service:**
   - File → Publish → Select workspace
   - Sign in to Power BI Service

2. **Configure Scheduled Refresh:**
   - Go to workspace → Find your dataset
   - Settings → Scheduled refresh
   - Set frequency: Daily at 1:00 AM (after midnight scraping completes)
   - Save

**Note:** Automatic refresh requires Power BI Pro or Premium license

---

## 🛠️ Data Transformation Tips

### Clean Price Data (If Needed)

If prices show as text:
```
1. Select price_gross column
2. Transform → Replace Values → Replace "€" with "" (empty)
3. Transform → Replace Values → Replace "," with "."
4. Transform → Data Type → Decimal Number
```

### Filter Out Empty Rows
```
1. Select any column
2. Home → Remove Rows → Remove Blank Rows
```

### Create Price Ranges
```
1. Add Column → Custom Column
2. Name: Price Range
3. Formula:
   if [price_gross] < 50 then "Under €50"
   else if [price_gross] < 100 then "€50-€100"
   else if [price_gross] < 500 then "€100-€500"
   else if [price_gross] < 1000 then "€500-€1000"
   else "Over €1000"
```

### Extract Domain from URL
```
1. Select product_url column
2. Add Column → Custom Column
3. Name: Domain
4. Formula: Text.BetweenDelimiters([product_url], "//", "/")
```

---

## 📈 Useful DAX Measures

### Total Products
```dax
Total Products = COUNTROWS('All Products')
```

### Average Price
```dax
Average Price = AVERAGE('All Products'[price_gross])
```

### Median Price
```dax
Median Price = MEDIAN('All Products'[price_gross])
```

### Products by Source
```dax
Products by Source = 
CALCULATE(
    COUNTROWS('All Products'),
    ALLEXCEPT('All Products', 'All Products'[source])
)
```

### Price Comparison (vs Average)
```dax
Price vs Average = 
'All Products'[price_gross] - [Average Price]
```

### Cheapest Supplier
```dax
Cheapest Supplier = 
CALCULATE(
    MIN('All Products'[source]),
    FILTER(
        'All Products',
        'All Products'[price_gross] = MIN('All Products'[price_gross])
    )
)
```

### Product Count by Category
```dax
Products in Category = 
CALCULATE(
    COUNTROWS('All Products'),
    ALLEXCEPT('All Products', 'All Products'[category])
)
```

---

## 🎯 Advanced Features

### 1. Price Comparison Across Suppliers

Create a matrix showing same products across different suppliers:

- Visual: Matrix
- Rows: name (or article_number)
- Columns: source
- Values: price_gross (Min)

### 2. Price Trend Analysis (If Historical Data Available)

If you keep historical data:

- Visual: Line Chart
- Axis: Date
- Legend: source
- Values: price_gross (Average)

### 3. Search Functionality

Add a slicer for product search:

- Visual: Slicer
- Field: name
- Slicer Settings → Search → Enable

### 4. Dynamic Filtering

Add slicers for:
- Category
- Manufacturer
- Price Range
- Supplier (source)

Users can filter the entire dashboard interactively.

---

## 🔍 Use Cases

### 1. Find Cheapest Supplier for Specific Product
- Filter by product name
- Sort by price_gross
- See which supplier has best price

### 2. Compare Average Prices by Category
- Group by category
- Calculate average price per supplier
- Identify which supplier is cheapest for each category

### 3. Identify Price Outliers
- Create scatter plot: price_gross vs. category
- Spot unusually high/low prices
- Investigate potential data errors or deals

### 4. Supplier Performance Dashboard
- Products per supplier
- Average price per supplier
- Category coverage per supplier

### 5. Product Catalog Export
- Filter products by criteria
- Export to Excel
- Share with team

---

## 📱 Mobile App

Power BI has mobile apps for iOS and Android:

1. Download Power BI app
2. Sign in with your account
3. Access your dashboards on the go
4. Get notifications for data updates

---

## 🆘 Troubleshooting

### Can't Load Google Sheets?

**Solution 1:** Use CSV export URLs (Method 1 above)
**Solution 2:** Make sure sheets are shared with your Google account
**Solution 3:** Check internet connection

### Data Not Updating?

1. Click **Refresh** button in Power BI Desktop
2. Check that scrapers ran successfully (check cron logs)
3. Verify Google Sheets have new data

### Too Much Data / Slow Performance?

1. Filter data in Power Query before loading
2. Remove unnecessary columns
3. Use aggregated views instead of row-level data
4. Consider Power BI Premium for better performance

### Price Column Shows as Text?

1. Transform Data → Select price_gross
2. Transform → Data Type → Decimal Number

### Duplicate Products Appearing?

1. Check if same product exists in multiple sheets
2. Use article_number or EAN to deduplicate
3. Create unique key: source + article_number

---

## 📚 Learning Resources

### Power BI Tutorials
- Official docs: https://docs.microsoft.com/power-bi/
- Free training: https://powerbi.microsoft.com/learning/
- Community: https://community.powerbi.com/

### YouTube Channels
- Guy in a Cube
- SQLBI
- Curbal

### Sample Reports
- Power BI Gallery: https://community.powerbi.com/t5/Data-Stories-Gallery/bd-p/DataStoriesGallery

---

## 🎓 Next Steps

1. ✅ Connect your first sheet (meinhausshop)
2. ✅ Create basic table visualization
3. ✅ Add all 9 sheets
4. ✅ Combine into one dataset
5. ✅ Create key metrics (cards)
6. ✅ Build price comparison charts
7. ✅ Add filters and slicers
8. ✅ Publish to Power BI Service (optional)
9. ✅ Set up auto-refresh (optional)
10. ✅ Share with team

---

## 💡 Pro Tips

1. **Use Bookmarks** - Save different views of your dashboard
2. **Add Tooltips** - Show additional info on hover
3. **Use Drill-Through** - Click a product to see details
4. **Create Mobile Layout** - Optimize for phone viewing
5. **Set Up Alerts** - Get notified when prices change
6. **Use Parameters** - Let users choose data refresh frequency
7. **Add Images** - Show product images from product_image column

---

## 📞 Support

**For Power BI Issues:**
- Microsoft Support: https://support.microsoft.com/power-bi
- Community Forum: https://community.powerbi.com/

**For Scraper/Data Issues:**
- Check logs: `logs/` directory
- Check cron logs: `cron_logs/`
- Verify Google Sheets are updating

---

**You're ready to build powerful price comparison dashboards!** 🚀

Start with one sheet, create a few visuals, then expand from there. Power BI makes it easy to analyze 333,000+ products and find the best deals.
