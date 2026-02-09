# Quick Start: Email Notifications

Get email alerts for product changes in 5 minutes!

## Step 1: Get Gmail App Password (2 minutes)

1. Go to https://myaccount.google.com/security
2. Click **"2-Step Verification"** → Turn it ON if not already
3. Search for **"App passwords"** or go to https://myaccount.google.com/apppasswords
4. Select:
   - App: **Mail**
   - Device: **Windows Computer** (or your device)
5. Click **Generate**
6. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)

## Step 2: Configure Email (1 minute)

1. **Open `email_config.py`** in your editor

2. **Update these 3 lines:**

```python
SENDER_EMAIL = "your-email@gmail.com"  # ← Your Gmail address
SENDER_PASSWORD = "abcd efgh ijkl mnop"  # ← The 16-char password from Step 1
RECIPIENT_EMAILS = ["your-email@gmail.com"]  # ← Where to send notifications
```

3. **Save the file**

## Step 3: Test It (1 minute)

Run this command:

```bash
python test_email_notifications.py
```

You should see:
```
✅ SUCCESS!
Test email sent successfully!
```

**Check your email!** You should receive a test email.

## Step 4: Run Scrapers with Notifications (1 minute)

```bash
python run_scrapers_with_notifications.py
```

This will:
1. ✅ Run all your scrapers
2. ✅ Compare with previous data
3. ✅ Send email if changes detected

## Step 5: Schedule Daily (Optional)

### Windows:

1. Open **Task Scheduler**
2. **Create Basic Task**
3. Name: "Daily Scraper Notifications"
4. Trigger: **Daily** at **2:00 AM**
5. Action: **Start a program**
   - Program: `python`
   - Arguments: `run_scrapers_with_notifications.py`
   - Start in: `C:\path\to\your\scrapers`
6. Click **Finish**

### Linux/Mac:

```bash
crontab -e
```

Add this line:
```
0 2 * * * cd /path/to/scrapers && python run_scrapers_with_notifications.py
```

## What You'll Get

### Email Subject:
```
🔔 MEINHAUSSHOP - 23 Changes Detected
```

### Email Content:
- **Summary:** New: 15, Updated: 8, Removed: 0
- **New Products Table:** All new products with prices
- **Updated Products Table:** What changed (prices, names, etc.)
- **Removed Products Table:** Products no longer available

### Price Changes Highlighted:
- 🔴 **Red** = Price increased
- 🟢 **Green** = Price decreased

## Troubleshooting

### "Authentication failed"
- ✅ Use **App Password**, not your regular Gmail password
- ✅ Make sure 2-Step Verification is enabled
- ✅ Generate a new App Password

### "No email received"
- ✅ Check spam/junk folder
- ✅ Wait 2-3 minutes (email can be delayed)
- ✅ Verify recipient email is correct

### "No changes detected"
- ✅ This is normal on first run!
- ✅ Run scraper again tomorrow to see changes
- ✅ System needs baseline data first

## Using Other Email Providers

### Outlook/Hotmail:
```python
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@outlook.com"
SENDER_PASSWORD = "your-regular-password"  # No app password needed
```

### Yahoo:
```python
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@yahoo.com"
SENDER_PASSWORD = "your-app-password"  # Generate at Yahoo security settings
```

## Need Help?

1. **Run the test:** `python test_email_notifications.py`
2. **Check the full guide:** `EMAIL_NOTIFICATIONS_SETUP.md`
3. **Review error messages** in the console

## Example Email Preview

```
📊 Scraper Update Report: MEINHAUSSHOP
Date: 2026-01-29 14:30:00

Summary
• New Products: 15
• Updated Products: 8  
• Removed Products: 2

🆕 New Products
┌─────────────────────────────────────────────────────────┐
│ Name              │ Manufacturer │ Price    │ Link      │
├─────────────────────────────────────────────────────────┤
│ DAB Nova Up 300   │ DAB          │ €189.90  │ View      │
│ Tallas D-CWP 300  │ Tallas       │ €119.00  │ View      │
└─────────────────────────────────────────────────────────┘

🔄 Updated Products
┌─────────────────────────────────────────────────────────┐
│ Name              │ Changed      │ Old → New            │
├─────────────────────────────────────────────────────────┤
│ Pump XYZ          │ price_gross  │ €150.00 → €139.90 ✓  │
└─────────────────────────────────────────────────────────┘
```

---

**That's it!** You're now getting automated email notifications for all product changes. 🎉
