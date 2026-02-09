# Power BI Import Instructions for Google Sheets

## Problem
When importing from Google Sheets to Power BI, the headers are not recognized and price columns are treated as text instead of numbers.

## Solution

### Step 1: Get the Google Sheets URL
Your Power BI test sheet ID: `1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA`

Full URL: `https://docs.google.com/spreadsheets/d/1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA/edit`

### Step 2: Import into Power BI

1. **Open Power BI Desktop**

2. **Get Data from Web**
   - Click "Get Data" → "Web"
   - Enter the Google Sheets URL (you may need to make it public or use the export URL)
   - Alternative: Use this export URL format:
     ```
     https://docs.google.com/spreadsheets/d/1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA/export?format=csv
     ```

3. **Transform Data (Power Query Editor)**
   - After loading, Power BI will open the Power Query Editor
   - You should see your data with Column1, Column2, etc.

4. **Promote First Row as Headers**
   - In the Power Query Editor ribbon, click "Transform" tab
   - Click "Use First Row as Headers"
   - Your column names should now appear correctly

5. **Change Data Types for Price Columns**
   - Click on the `price_net` column header
   - In the ribbon, click "Data Type" dropdown
   - Select "Decimal Number"
   - Repeat for `price_gross` column

6. **Apply Changes**
   - Click "Close & Apply" in the top left
   - Your data is now ready with proper headers and numeric price columns

### Step 3: Verify
- Check that column names are correct (manufacturer, category, name, etc.)
- Check that price_net and price_gross show the Σ (sum) icon indicating they're numbers
- Try sorting by price_gross - it should sort numerically

## Alternative: Use CSV Export URL

If the above doesn't work, use the CSV export URL directly:

```
https://docs.google.com/spreadsheets/d/1jdJaz4su4OGoZr1hx4dmlhMp85Onp0_p1r8_KugvoZA/export?format=csv&gid=0
```

This will automatically:
- Include headers in the first row
- Export numbers as numbers (not text)

Then in Power BI:
1. Get Data → Web → Enter the CSV export URL above
2. Power BI should automatically detect headers and data types
3. If not, follow steps 4-6 above

## Troubleshooting

### Headers Still Not Showing
- Make sure you clicked "Use First Row as Headers" in Power Query Editor
- Check that the first row in Google Sheets actually contains the header names

### Prices Still Not Sortable
- In Power Query Editor, manually set the data type to "Decimal Number"
- Make sure the price values in the sheet are actual numbers (not text with quotes)
- Check that there are no special characters or currency symbols in the price cells

### Can't Access Google Sheet
- Make sure the sheet is shared with "Anyone with the link can view"
- Or use the CSV export URL which works even for private sheets if you're logged in

## Quick Test
To verify your data is correct in Google Sheets:
1. Open the sheet in your browser
2. Click on a price_gross cell
3. Check if it shows as a number (right-aligned) or text (left-aligned)
4. Numbers should be right-aligned and sortable in Google Sheets itself
