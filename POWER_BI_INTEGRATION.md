# Power BI Integration Guide - Complete Setup

Complete guide to connect your 9 web scrapers to Power BI for price comparison dashboards.

## 📊 Overview

Your scraping system collects ~283,000+ products from 9 websites every night and pushes them to Google Sheets. Power BI can connect to these sheets to create interactive dashboards for price comparison and analysis.

---

## 🔗 Your Google Sheets

All data is automatically updated nightly at midnight:

| Website | Products | Sheet URL |
|---------|----------|-----------|
| **meinhausshop.de** | ~169,000 | [Open Sheet](https://docs.google.com/spreadsheets/d/1KaMWOGh9KEPvvxWQRKLu-fLr0-aSLdhn5IbdZ0XyvTQ) |
| **heima24.de** | ~24,500 | [Open Sheet](https://docs.google.com/spreadsheets/d/1nfHVN4RZM-tED-HtXUWV7bwtAWjctih7dJ2eOyTRj08) |
| **sanundo.de** | ~21,200 | [Open Sheet](https://docs.google.com/spreadsheets/d/1ygsm7nK3glzapTCoM0X7Hk3x1-xY3ieTqRCdXJN5Y8A) |
| **heizungsdiscount24.de** | ~68,300 | [Open Sheet](https://docs.google.com/spreadsheets/d/1dwls46f4xW7Td5XrV8ShvLdwsPJwQhPieH342BOEZ8o) |
| **wolfonlineshop.de** | ~160 | [Open Sheet](https://docs.google.com/spreadsheets/d/1IR3BAObUJf4cUxdX9OF1zka0YsOrP35c-n8F4xIl3a8) |
| **st-shop24.de** | ~243 | [Open Sheet](https://docs.google.com/spreadsheets/d/1inV05kOmYe53iq0ujyDafftzxZgqWVnBriRbD-BOd_k) |
| **selfio.de** | ~13,300 | [Open Sheet](https://docs.google.com/spreadsheets/d/19evdUWIJX9hLK46XYp5avvlW9KZhGayjnw6fkwn2CfE) |
| **pumpe24.de** | ~45 | [Open Sheet](https://docs.google.com/spreadsheets/d/1eKkepxz9FtDVQNaQmBmPfnTqTcFz7kai0dxJ0JCwuGU) |
| **wasserpumpe.de** | ~10,800 | [Open Sheet](https://docs.google.com/spreadsheets/d/1iGmt66Y4mKwC06aT0NhKzWZ8GfcCtgY0oPdYVSY4Jz4) |

**Total: ~283,000+ products updated nightly**

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Power BI Desktop

Download and install (free):
- https://powerbi.microsoft.com/desktop/

### Step 2: Connect First Sheet

1. Open Power BI Desktop
2. Click **"Get Data"** → Search **"Google Sheets"**
3. Click **"Connect"**
4. Sign in with your Google account
5. Paste sheet URL (start with wolfonlineshop - smallest dataset)
6. Select **"Sheet1"** → Click **"Load"**

### Step 3: Create First Visual

1. Click **"Table"** visualization
2. Drag these fields to the table:
   - manufacturer
   - name
   - price_gross
   - category
3. Done! You have your first visual.

---

## 📈 Complete Setup - All 9 Scrapers

### Method 1: Connect All Sheets Individually

**For each sheet:**

1. **Home** → **Get Data** → **Google Sheets**
2. Paste sheet URL
3. Select **"Sheet1"**
4. Click **"Load"**
5. Rename query to website name (e.g., "meinhausshop")

**Repeat for all 9 sheets.**

### Method 2: Combine All Data (Recommended)

After loading all sheets:

1. **Home** → **Transform Data** (opens Power Query Editor)
2. Select first query (e.g., "wolfonlineshop")
3. **Add Column** → **Custom Column**
   - Name: `Source`
   - Formula: `"wolfonlineshop"`
4. Repeat step 3 for each query with respective names
5. **Home** → **Append Queries** → **Append Queries as New**
6. Select all 9 queries
7. Click **OK**
8. Rename new query to **"All Products"**
9. **Home** → **Close & Apply**

Now you have one unified dataset with all 283,000+ products!

---

## 🎨 Dashboard Examples

### Dashboard 1: Price Comparison

**Visuals to create:**

1. **Card: Total Products**
   - Field: `name` (Count)
   - Shows: 283,000+

2. **Card: Average Price**
   - Field: `price_gross` (Average)
   - Format: Currency (€)

3. **Bar Chart: Products by Website**
   - Axis: `Source`
   - Values: `name` (Count)
   - Shows: Which site has most products

4. **Table: Top 10 Cheapest Products**
   - Fields: `Source`, `name`, `price_gross`, `product_url`
   - Filter: Top 10 by `price_gross` (ascending)

5. **Scatter Chart: Price vs Category**
   - X-Axis: `category`
   - Y-Axis: `price_gross`
   - Details: `name`

### Dashboard 2: Category Analysis

1. **Treemap: Products by Category**
   - Group: `category`
   - Values: `name` (Count)

2. **Line Chart: Average Price by Category**
   - Axis: `category`
   - Values: `price_gross` (Average)

3. **Table: Category Summary**
   - Rows: `category`
   - Values: 
     - `name` (Count)
     - `price_gross` (Average)
     - `price_gross` (Min)
     - `price_gross` (Max)

### Dashboard 3: Manufacturer Comparison

1. **Bar Chart: Top 20 Manufacturers**
   - Axis: `manufacturer`
   - Values: `name` (Count)
   - Filter: Top 20

2. **Table: Manufacturer Price Ranges**
   - Rows: `manufacturer`
   - Values:
     - `price_gross` (Average)
     - `price_gross` (Min)
     - `price_gross` (Max)

---

## 🔄 Data Transformation (Power Query)

### Clean Price Data

If prices have currency symbols:

```
1. Select "price_gross" column
2. Transform → Replace Values
   - Value to Find: "€"
   - Replace With: (empty)
3. Transform → Replace Values
   - Value to Find: ","
   - Replace With: "."
4. Transform → Data Type → Decimal Number
```

### Remove Empty Rows

```
1. Home → Remove Rows → Remove Blank Rows
```

### Add Price Categories

```
1. Add Column → Custom Column
2. Name: "Price Range"
3. Formula:
   if [price_gross] < 50 then "Under €50"
   else if [price_gross] < 100 then "€50-€100"
   else if [price_gross] < 500 then "€100-€500"
   else if [price_gross] < 1000 then "€500-€1000"
   else "Over €1000"
```

### Extract Product Type from Name

```
1. Select "name" column
2. Transform → Extract → Text Before Delimiter
3. Delimiter: " " (space)
4. Rename to "Product Type"
```

---

## 📊 Useful DAX Measures

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

### Price Range
```dax
Price Range = MAX('All Products'[price_gross]) - MIN('All Products'[price_gross])
```

### Products Under €100
```dax
Budget Products = 
CALCULATE(
    COUNTROWS('All Products'),
    'All Products'[price_gross] < 100
)
```

### Average Price by Source
```dax
Avg Price by Source = 
CALCULATE(
    AVERAGE('All Products'[price_gross]),
    ALLEXCEPT('All Products', 'All Products'[Source])
)
```

### Price Comparison (vs Average)
```dax
Price vs Average = 
'All Products'[price_gross] - [Average Price]
```

### Cheapest Product
```dax
Cheapest Product = 
CALCULATE(
    MIN('All Products'[price_gross])
)
```

### Most Expensive Product
```dax
Most Expensive Product = 
CALCULATE(
    MAX('All Products'[price_gross])
)
```

---

## 🔄 Auto-Refresh Setup

### Power BI Desktop (Manual Refresh)

Click **"Refresh"** button anytime to get latest data from Google Sheets.

### Power BI Service (Automatic Refresh)

**Requirements:**
- Power BI Pro or Premium license
- Publish report to Power BI Service

**Setup:**

1. **Publish Report:**
   - File → Publish → Publish to Power BI
   - Select workspace
   - Click "Publish"

2. **Configure Gateway (if needed):**
   - For Google Sheets, usually not required
   - Data refreshes directly from cloud

3. **Schedule Refresh:**
   - Go to Power BI Service (app.powerbi.com)
   - Navigate to your dataset
   - Settings → Scheduled refresh
   - Configure:
     - Frequency: Daily
     - Time: 2:00 AM (after scrapers finish)
     - Time zone: Your timezone
   - Click "Apply"

**Refresh Frequency Options:**
- Daily (recommended)
- Weekly
- Up to 8 times per day (Pro)
- Up to 48 times per day (Premium)

---

## 🎯 Sample Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Heating & Plumbing Equipment Price Comparison                  │
│  Last Updated: 2026-01-28 02:00 AM                             │
├──────────────┬──────────────┬──────────────┬──────────────────┤
│ Total        │ Avg Price    │ Cheapest     │ Most Expensive   │
│ Products     │ €234.50      │ €5.99        │ €15,999.00      │
│ 283,456      │              │              │                  │
├──────────────┴──────────────┴──────────────┴──────────────────┤
│                                                                 │
│  Products by Website (Bar Chart)                               │
│  meinhausshop     ████████████████████████████ 169,000        │
│  heizungsdiscount ████████████ 68,300                         │
│  heima24          ████ 24,500                                 │
│  sanundo          ███ 21,200                                  │
│  selfio           ██ 13,300                                   │
│  wasserpumpe      █ 10,800                                    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Top 10 Cheapest Products (Table)                             │
│  Source        │ Product Name      │ Price  │ Category        │
│  meinhausshop  │ O-Ring 10mm      │ €5.99  │ Fittings       │
│  sanundo       │ Screw Set        │ €7.50  │ Hardware       │
│  heima24       │ Gasket 1/2"      │ €8.99  │ Seals          │
│  ...                                                           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Average Price by Category (Column Chart)                      │
│  █████ Boilers (€2,500)                                       │
│  ████ Heat Pumps (€1,800)                                     │
│  ███ Radiators (€450)                                         │
│  ██ Valves (€85)                                              │
│  █ Fittings (€25)                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Visualization Best Practices

### For Large Datasets (169k+ products)

1. **Use Filters:**
   - Add slicers for Category, Manufacturer, Price Range
   - Filter to specific product types

2. **Aggregate Data:**
   - Show averages, not individual products
   - Group by category or manufacturer

3. **Use Top N Filters:**
   - Top 100 products by price
   - Top 20 manufacturers
   - Top 10 categories

4. **Performance Tips:**
   - Import mode (not DirectQuery)
   - Remove unnecessary columns
   - Use summarized tables

### Color Schemes

**Recommended:**
- Blue: meinhausshop
- Green: heima24
- Orange: sanundo
- Red: heizungsdiscount24
- Purple: selfio
- Teal: wolfonlineshop
- Yellow: st-shop24
- Pink: pumpe24
- Brown: wasserpumpe

---

## 🔍 Advanced Analysis Examples

### Price Comparison by Product

Find same product across multiple sites:

```dax
Product Comparison = 
CALCULATE(
    COUNTROWS('All Products'),
    FILTER(
        'All Products',
        'All Products'[article_number] = EARLIER('All Products'[article_number])
    )
) > 1
```

### Best Price Finder

```dax
Best Price = 
CALCULATE(
    MIN('All Products'[price_gross]),
    ALLEXCEPT('All Products', 'All Products'[article_number])
)
```

### Price Difference from Cheapest

```dax
Price Difference = 
'All Products'[price_gross] - [Best Price]
```

### Savings Percentage

```dax
Savings % = 
DIVIDE(
    [Price Difference],
    'All Products'[price_gross],
    0
) * 100
```

---

## 📱 Mobile Dashboard

Power BI automatically creates mobile layouts, but you can optimize:

1. **Report View** → **Mobile Layout**
2. Drag visuals to mobile canvas
3. Prioritize:
   - Key metrics (cards)
   - Simple charts (bar, line)
   - Filtered tables
4. Avoid:
   - Complex visuals
   - Too many filters
   - Small text

---

## 🛠️ Troubleshooting

### Connection Issues

**Problem:** Can't connect to Google Sheets
**Solution:**
- Sign in with correct Google account
- Ensure sheets are shared with your account
- Check internet connection

**Problem:** "Couldn't refresh the entity" error
**Solution:**
- Re-authenticate Google account
- Check if sheet still exists
- Verify sheet permissions

### Performance Issues

**Problem:** Power BI slow with 283k products
**Solution:**
- Use filters and slicers
- Aggregate data (show averages, not all rows)
- Remove unused columns in Power Query
- Use Import mode, not DirectQuery

**Problem:** Refresh takes too long
**Solution:**
- Refresh only changed data
- Schedule refresh during off-hours
- Consider incremental refresh (Premium feature)

### Data Issues

**Problem:** Prices showing as text
**Solution:**
- Power Query → Select price column
- Transform → Data Type → Decimal Number

**Problem:** Empty rows
**Solution:**
- Power Query → Remove Blank Rows

**Problem:** Duplicate products
**Solution:**
- Power Query → Remove Duplicates
- Or use article_number as unique key

---

## 📚 Learning Resources

### Power BI Basics
- Official docs: https://docs.microsoft.com/power-bi/
- Free training: https://powerbi.microsoft.com/learning/
- Community: https://community.powerbi.com/

### DAX (Data Analysis Expressions)
- DAX Guide: https://dax.guide/
- DAX Patterns: https://www.daxpatterns.com/

### Power Query (M Language)
- M Reference: https://docs.microsoft.com/powerquery-m/

---

## 🎯 Next Steps

1. ✅ Install Power BI Desktop
2. ✅ Connect first sheet (wolfonlineshop - smallest)
3. ✅ Create basic table visual
4. ✅ Connect remaining 8 sheets
5. ✅ Combine all data with "Append Queries"
6. ✅ Add "Source" column to identify websites
7. ✅ Create price comparison dashboard
8. ✅ Add filters and slicers
9. ✅ Publish to Power BI Service (optional)
10. ✅ Schedule auto-refresh (optional)

---

## 💡 Pro Tips

1. **Start Small:** Connect wolfonlineshop first (only 160 products) to learn
2. **Use Bookmarks:** Save different views of your dashboard
3. **Add Tooltips:** Show detailed info on hover
4. **Use Drill-Through:** Click category to see all products
5. **Create Parameters:** Let users choose price ranges dynamically
6. **Add Last Refresh Time:** Show when data was last updated
7. **Use Conditional Formatting:** Highlight best prices in green
8. **Create Mobile View:** Optimize for phone/tablet viewing

---

## 📊 Sample Report Template

Want a pre-built template? Here's what to include:

**Page 1: Overview**
- Total products card
- Average price card
- Products by website bar chart
- Price distribution histogram

**Page 2: Price Comparison**
- Top 10 cheapest table
- Top 10 most expensive table
- Price by category chart
- Filters: Category, Manufacturer, Price Range

**Page 3: Category Analysis**
- Products by category treemap
- Average price by category
- Category details table

**Page 4: Manufacturer Analysis**
- Top manufacturers bar chart
- Manufacturer price comparison
- Product count by manufacturer

**Page 5: Product Search**
- Search box (filter)
- Detailed product table
- Product details card

---

## ✅ Summary

You now have:
- ✓ 9 Google Sheets with 283,000+ products
- ✓ Automatic nightly updates at midnight
- ✓ Power BI connection instructions
- ✓ Dashboard examples and templates
- ✓ DAX measures for analysis
- ✓ Auto-refresh setup guide

**Your data is ready for Power BI - start building your dashboards!** 🚀
