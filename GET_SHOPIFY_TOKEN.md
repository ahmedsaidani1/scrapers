# How to Get Your Shopify API Token

## Step-by-Step Guide for tbbt.de

### Step 1: Log in to Shopify Admin

Go to: **https://tbbt.myshopify.com/admin**

(Or click "Admin" from your store dashboard)

---

### Step 2: Navigate to Apps Settings

1. Click **Settings** (bottom left, gear icon)
2. Click **Apps and sales channels**
3. Click **Develop apps** (top right)

**Note:** If you don't see "Develop apps", you may need to enable it:
- Click **"Allow custom app development"**
- Confirm the action

---

### Step 3: Create a New App

1. Click **Create an app** button
2. Enter app name: `Product Scraper Integration`
3. Click **Create app**

---

### Step 4: Configure API Scopes (Permissions)

1. Click **Configure Admin API scopes**
2. Scroll down and check these permissions:
   - ☑ `read_products`
   - ☑ `write_products`
   - ☑ `read_inventory`
   - ☑ `write_inventory`
3. Click **Save** button

---

### Step 5: Install the App

1. Click **Install app** button (top right)
2. Confirm the installation

---

### Step 6: Get Your API Token

After installation, you'll see:

**Admin API access token**
```
shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ **IMPORTANT:** 
- This token is shown **ONLY ONCE**
- Copy it immediately
- Store it securely
- If you lose it, you'll need to regenerate a new one

---

### Step 7: Copy the Token

Click **Reveal token once** and copy the entire token.

It will look like:
```
shpat_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

---

### Step 8: Update Configuration

Open `shopify_config.py` and paste your token:

```python
SHOPIFY_CONFIG = {
    'shop_url': 'tbbt.myshopify.com',  # ✓ Already configured
    'api_key': 'ecbc15c5ffeffec3a5a551ef6a1a71a3',  # ✓ Already configured
    'api_password': 'shpat_xxxxx',  # ← PASTE YOUR TOKEN HERE
    # ...
}
```

---

### Step 9: Test Connection

Run the test script:

```bash
python test_shopify_connection.py
```

You should see:
```
✓ Configuration valid
✓ Connection successful
✓ All tests passed!
```

---

## Quick Navigation Path

```
Shopify Admin
  └─ Settings (⚙️)
      └─ Apps and sales channels
          └─ Develop apps
              └─ Create an app
                  └─ Configure Admin API scopes
                      └─ Install app
                          └─ Reveal token once
```

---

## Troubleshooting

### "I don't see 'Develop apps'"

You need to enable custom app development:
1. Go to Settings → Apps and sales channels
2. Look for "App development" section
3. Click "Allow custom app development"
4. Confirm

### "I lost my token"

No problem! You can regenerate it:
1. Go to Settings → Apps and sales channels → Develop apps
2. Click on your app name
3. Go to "API credentials" tab
4. Click "Regenerate token"
5. Copy the new token

### "Permission denied errors"

Make sure you enabled all 4 scopes:
- read_products
- write_products
- read_inventory
- write_inventory

---

## Security Reminder

🔒 **Keep your token secure:**
- Never share it publicly
- Don't commit it to Git (already in .gitignore)
- Treat it like a password
- Rotate it periodically

---

## What's Next?

Once you have your token configured:

1. **Test connection:**
   ```bash
   python test_shopify_connection.py
   ```

2. **Test sync (5 products):**
   ```bash
   python sync_all_to_shopify.py --test
   ```

3. **Review products in Shopify admin**

4. **Run full sync:**
   ```bash
   python sync_all_to_shopify.py
   ```

---

## Need Help?

If you get stuck:
1. Check the Shopify admin URL is correct: `tbbt.myshopify.com`
2. Verify all 4 API scopes are enabled
3. Make sure you copied the entire token (starts with `shpat_`)
4. Try regenerating the token if connection fails

For more details, see: `SHOPIFY_INTEGRATION_SETUP.md`
