# Power BI Dashboard - Complete Step-by-Step Tutorial

This guide will walk you through creating the exact dashboard layout, from loading data to final visualizations.

---

## 🎯 Final Result

You'll build a dashboard with:
- ✅ 4 key metric cards (Total Products, Avg Price, Suppliers, Last Updated)
- ✅ Bar chart showing average price by supplier
- ✅ Pie chart showing products by category
- ✅ Table showing top 10 cheapest products
- ✅ Searchable table with all products

**Time needed: 20-30 minutes**

---

## PART 1: Load All Your Data

### Step 1: Open Power BI Desktop

1. Launch **Power BI Desktop**
2. Close the welcome screen if it appears
3. You should see a blank canvas

### Step 2: Load First Sheet (meinhausshop)

1. Click **"Get data"** button (top ribbon)
2. Search for **"Web"** and select it
3. Click **"Connect"**
4. Choose **"Basic"** tab
5. Paste this URL:
   ```
   https://docs.google.com/spreadsheets/d/1KaMWOGh9KEPvvxWQRKLu-fLr0-aSLdhn5IbdZ0XyvTQ/export?format=csv
   ```
6. Click **"OK"**
7. Preview appears → Click **"Transform Data"** (NOT "Load" yet!)

### Step 3: Add Source Column

In the Power Query Editor that opens:

1. Click **"Add Column"** tab (top ribbon)
2. Click **"Custom Column"**
3. New column name: `source`
4. Formula: `"meinhausshop"`
5. Click **"OK"**
6. You should see a new "source" column with "meinhausshop" in every row

### Step 4: Rename Query

1. On the left side, right-click the query (probably named "Table")
2. Select **"Rename"**
3. Type: `meinhausshop`
4. Press Enter

### Step 5: Load Remaining 8 Sheets

Repeat Steps 2-4 for each sheet below. **Important:** Change the URL and source name each time!

**heima24:**
- URL: `https://docs.google.com/spreadsheets/d/1nfHVN4RZM-tED-HtXUWV7bwtAWjctih7dJ2eOyTRj08/export?format=csv`
- Source: `"heima24"`

**sanundo:**
- URL: `https://docs.google.com/spreadsheets/d/1ygsm7nK3glzapTCoM0X7Hk3x1-xY3ieTqRCdXJN5Y8A/export?format=csv`
- Source: `"sanundo"`

**heizungsdiscount24:**
- URL: `https://docs.google.com/spreadsheets/d/1dwls46f4xW7Td5XrV8ShvLdwsPJwQhPieH342BOEZ8o/export?format=csv`
- Source: `"heizungsdiscount24"`

**wolfonlineshop:**
- URL: `https://docs.google.com/spreadsheets/d/1IR3BAObUJf4cUxdX9OF1zka0YsOrP35c-n8F4xIl3a8/export?format=csv`
- Source: `"wolfonlineshop"`

**st_shop24:**
- URL: `https://docs.google.com/spreadsheets/d/1inV05kOmYe53iq0ujyDafftzxZgqWVnBriRbD-BOd_k/export?format=csv`
- Source: `"st_shop24"`

**selfio:**
- URL: `https://docs.google.com/spreadsheets/d/19evdUWIJX9hLK46XYp5avvlW9KZhGayjnw6fkwn2CfE/export?format=csv`
- Source: `"selfio"`

**pumpe24:**
- URL: `https://docs.google.com/spreadsheets/d/1eKkepxz9FtDVQNaQmBmPfnTqTcFz7kai0dxJ0JCwuGU/export?format=csv`
- Source: `"pumpe24"`

**wasserpumpe:**
- URL: `https://docs.google.com/spreadsheets/d/1iGmt66Y4mKwC06aT0NhKzWZ8GfcCtgY0oPdYVSY4Jz4/export?format=csv`
- Source: `"wasserpumpe"`

### Step 6: Combine All Sheets

Now you should have 9 queries in the left panel. Let's combine them:

1. Select the first query (**meinhausshop**)
2. Click **"Home"** tab → **"Append Queries"** → **"Append Queries as New"**
3. Select **"Three or more tables"**
4. In the right panel, add all 9 queries:
   - meinhausshop
   - heima24
   - sanundo
   - heizungsdiscount24
   - wolfonlineshop
   - st_shop24
   - selfio
   - pumpe24
   - wasserpumpe
5. Click **"OK"**
6. A new query appears named "Append1"
7. Right-click it → Rename to **"All Products"**

### Step 7: Load Data

1. Click **"Home"** tab → **"Close & Apply"**
2. Wait for data to load (may take 1-2 minutes for 333k products)
3. You're back to the main Power BI canvas

---

## PART 2: Create the Dashboard

### Layout Overview

We'll create 3 rows:
- **Row 1:** 4 cards (metrics)
- **Row 2:** Bar chart (left) + Pie chart & Table (right)
- **Row 3:** Large searchable table

### Step 8: Create Card 1 - Total Products

1. Click **"Card"** visualization (right panel, looks like "123")
2. Drag **"name"** field to the card
3. It shows a number
4. Click the dropdown arrow on "name" → Select **"Count"** (not "Count (Distinct)")
5. Click **"Format"** (paint roller icon)
6. Expand **"Callout value"**
7. Change font size to **36**
8. Expand **"Category label"**
9. Turn it **On**
10. Change text to: `Total Products`
11. Resize and position card in top-left corner

### Step 9: Create Card 2 - Average Price

1. Click empty space on canvas
2. Click **"Card"** visualization
3. Drag **"price_gross"** field to the card
4. Click dropdown on "price_gross" → Select **"Average"**
5. Format:
   - Callout value font size: **36**
   - Category label: **On**
   - Category label text: `Avg Price`
   - Display units: **None**
   - Value decimal places: **0**
6. Position next to first card

### Step 10: Create Card 3 - Suppliers

1. Click empty space
2. Click **"Card"** visualization
3. Drag **"source"** field to the card
4. Click dropdown → Select **"Count (Distinct)"**
5. Format:
   - Callout value font size: **36**
   - Category label: **On**
   - Category label text: `Suppliers`
6. Position next to second card

### Step 11: Create Card 4 - Last Updated

1. Click empty space
2. Click **"Card"** visualization
3. Click **"Modeling"** tab → **"New Measure"**
4. In formula bar, type:
   ```
   Last Updated = "Today " & FORMAT(NOW(), "HH:mm")
   ```
5. Press Enter
6. Drag this new measure to the card
7. Format:
   - Callout value font size: **24**
   - Category label: **On**
   - Category label text: `Last Updated`
8. Position next to third card

### Step 12: Create Bar Chart - Average Price by Supplier

1. Click empty space (below the cards)
2. Click **"Clustered bar chart"** visualization
3. Drag **"source"** to **Y-axis**
4. Drag **"price_gross"** to **X-axis**
5. Click dropdown on price_gross → Select **"Average"**
6. Format:
   - Title: **On**
   - Title text: `Average Price by Supplier`
   - Data labels: **On**
   - Data labels position: **Outside end**
7. Resize to take up left half of row 2

### Step 13: Create Pie Chart - Products by Category

1. Click empty space (top-right of row 2)
2. Click **"Pie chart"** visualization
3. Drag **"category"** to **Legend**
4. Drag **"name"** to **Values**
5. Click dropdown on name → Select **"Count"**
6. Format:
   - Title: **On**
   - Title text: `Products by Category`
   - Legend: **On**
   - Legend position: **Right**
   - Data labels: **On**
   - Data labels show: **Category and percentage**
7. Resize to fit top-right area

### Step 14: Create Table - Top 10 Cheapest Products

1. Click empty space (below pie chart)
2. Click **"Table"** visualization
3. Drag these fields to the table (in order):
   - **name**
   - **price_gross**
   - **source**
4. Click the table visualization
5. Click **"Filters"** pane (right side)
6. Drag **"price_gross"** to **"Filters on this visual"**
7. Change filter type to **"Top N"**
8. Show items: **Top 10**
9. By value: **price_gross** (should auto-select)
10. Click **"Apply filter"**
11. Format:
    - Title: **On**
    - Title text: `Top 10 Cheapest Products`
    - Grid: **On**
    - Column headers font size: **12**
12. Resize to fit below pie chart

### Step 15: Create Searchable Table - All Products

1. Click empty space (bottom of canvas - row 3)
2. Click **"Table"** visualization
3. Drag these fields to the table:
   - **name**
   - **manufacturer**
   - **price_gross**
   - **category**
   - **source**
4. Format:
   - Title: **On**
   - Title text: `All Products (Searchable)`
   - Grid: **On**
   - Text size: **10**
5. Resize to take up entire bottom row (make it wide and tall)

### Step 16: Add Search Functionality

1. Click empty space above the large table
2. Click **"Slicer"** visualization
3. Drag **"name"** field to the slicer
4. Click the slicer
5. Click **"Format"** (paint roller)
6. Expand **"Slicer settings"**
7. Turn on **"Search"**
8. Style: **Dropdown**
9. Position above or beside the large table

### Step 17: Add Category Filter

1. Click empty space
2. Click **"Slicer"** visualization
3. Drag **"category"** to the slicer
4. Format:
   - Style: **Dropdown** or **List**
   - Search: **On**
5. Position next to name slicer

### Step 18: Add Supplier Filter

1. Click empty space
2. Click **"Slicer"** visualization
3. Drag **"source"** to the slicer
4. Format:
   - Style: **Dropdown** or **Tile**
   - Search: **On**
5. Position next to category slicer

---

## PART 3: Final Touches

### Step 19: Add Dashboard Title

1. Click **"Text box"** (Home tab → Text box)
2. Type: `Heating & Plumbing Equipment Price Comparison Dashboard`
3. Format:
   - Font size: **24**
   - Bold: **On**
   - Alignment: **Center**
4. Position at very top of canvas

### Step 20: Format Canvas

1. Click empty space on canvas
2. Click **"Format"** (paint roller)
3. Expand **"Canvas background"**
4. Color: Light gray (#F5F5F5) or white
5. Transparency: **0%**

### Step 21: Align Visualizations

1. Hold **Ctrl** and click multiple visualizations
2. **Format** tab → **Align** → Choose alignment option
3. Use **Distribute horizontally** and **Distribute vertically** for even spacing

### Step 22: Test Interactivity

1. Click on a bar in the bar chart → Other visuals filter
2. Click on a pie slice → Other visuals filter
3. Use the slicers to search and filter
4. Click **"Clear filters"** icon to reset

---

## PART 4: Save and Share

### Step 23: Save Your Work

1. **File** → **Save**
2. Choose location and filename: `Price Comparison Dashboard.pbix`
3. Click **"Save"**

### Step 24: Publish to Power BI Service (Optional)

1. Click **"Publish"** button (Home tab)
2. Sign in to Power BI Service
3. Select workspace
4. Click **"Select"**
5. Wait for upload
6. Click **"Open in Power BI"** to view online

### Step 25: Set Up Auto-Refresh (Optional - Requires Pro)

1. Go to Power BI Service (app.powerbi.com)
2. Find your dataset
3. Click **"..."** → **"Settings"**
4. Expand **"Scheduled refresh"**
5. Turn on **"Keep your data up to date"**
6. Set schedule: **Daily at 1:00 AM** (after midnight scraping)
7. Click **"Apply"**

---

## 🎨 Customization Tips

### Change Colors

1. Select a visualization
2. **Format** → **Data colors**
3. Choose custom colors for each supplier/category

### Add Conditional Formatting

For the large table:
1. Select the table
2. Click **"price_gross"** field
3. **Conditional formatting** → **Background color**
4. Set rules: Green for low prices, Red for high prices

### Add Drill-Through

1. Create a new page (bottom tabs)
2. Add detailed product information
3. Set up drill-through from main dashboard

### Add Bookmarks

1. **View** tab → **Bookmarks pane**
2. Create bookmarks for different views
3. Add buttons to switch between views

---

## 🔄 Refresh Data

### Manual Refresh

1. Click **"Refresh"** button (Home tab)
2. Data updates from Google Sheets
3. Takes 1-2 minutes

### Automatic Refresh

- Power BI Desktop: Manual only
- Power BI Service: Set up scheduled refresh (see Step 25)

---

## 🆘 Troubleshooting

### Visualizations Not Showing Data

- Check that "All Products" query is selected in Fields pane
- Verify data loaded successfully (check row count at bottom)

### Filters Not Working

- Make sure visualizations are using the same dataset
- Check filter pane for conflicting filters

### Slow Performance

- Reduce number of rows displayed in tables
- Use aggregated views instead of row-level data
- Close other applications

### Can't See All Fields

- Click **"All Products"** in Fields pane to expand
- Scroll down to see all columns

---

## ✅ Checklist

- [ ] All 9 sheets loaded with source column
- [ ] Sheets combined into "All Products"
- [ ] 4 metric cards created
- [ ] Bar chart showing price by supplier
- [ ] Pie chart showing products by category
- [ ] Top 10 cheapest products table
- [ ] Large searchable products table
- [ ] Slicers for search and filtering
- [ ] Dashboard title added
- [ ] Visualizations aligned and formatted
- [ ] File saved
- [ ] Tested interactivity

---

## 🎓 Next Steps

1. ✅ Add more visualizations (price trends, manufacturer analysis)
2. ✅ Create additional pages for detailed views
3. ✅ Set up alerts for price changes
4. ✅ Share with team
5. ✅ Schedule automatic refresh
6. ✅ Create mobile layout

---

**Congratulations! You've built a complete price comparison dashboard!** 🎉

Your dashboard now shows 333,000+ products from 9 suppliers with interactive filtering, search, and price comparisons. The data updates automatically every night at midnight.
