# Email Notifications Setup Guide

This guide will help you set up automated email notifications for your scrapers.

## Overview

The email notification system:
- ✅ Detects **new products** added to websites
- ✅ Detects **updated products** (price changes, name changes, etc.)
- ✅ Detects **removed products** (no longer available)
- ✅ Sends beautiful HTML email reports
- ✅ Tracks changes between scraping runs
- ✅ Works with any email provider (Gmail, Outlook, etc.)

## Quick Start

### Step 1: Install Required Package

```bash
pip install secure-smtplib
```

(This is usually already included with Python, but just in case)

### Step 2: Configure Email Settings

1. **Open `email_config.py`**

2. **For Gmail users:**
   - Go to https://myaccount.google.com/security
   - Enable **2-Step Verification**
   - Go to **App passwords** (search for it)
   - Select **Mail** and **Windows Computer**
   - Click **Generate**
   - Copy the 16-character password

3. **Update the configuration:**

```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "your-email@gmail.com"  # Your Gmail address
SENDER_PASSWORD = "abcd efgh ijkl mnop"  # The 16-char app password

RECIPIENT_EMAILS = [
    "recipient@example.com",  # Who should receive notifications
]
```

### Step 3: Test the Email System

Run the test script to make sure emails work:

```bash
python test_email_notifications.py
```

This will:
- Test your email configuration
- Send a test email
- Verify everything is working

### Step 4: Run Scrapers with Notifications

```bash
python run_scrapers_with_notifications.py
```

This will:
1. Run all configured scrapers
2. Compare results with previous run
3. Send email notifications for any changes

## Email Providers Configuration

### Gmail
```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# Use App Password (not regular password)
```

### Outlook/Hotmail
```python
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
# Use regular password
```

### Yahoo Mail
```python
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
# Use App Password
```

### Custom SMTP Server
```python
SMTP_SERVER = "your-smtp-server.com"
SMTP_PORT = 587  # or 465 for SSL
```

## What the Email Looks Like

The email notification includes:

### Summary Section
- Total new products
- Total updated products
- Total removed products

### New Products Table
- Product name
- Manufacturer
- Category
- Price
- Link to product

### Updated Products Table
- Product name
- What changed (price, name, etc.)
- Old value → New value
- Price changes highlighted (red for increase, green for decrease)
- Link to product

### Removed Products Table
- Products no longer available
- Last known price

## Customization Options

### Change Notification Threshold

In `email_config.py`:

```python
# Only send email if at least 5 changes detected
MIN_CHANGES_THRESHOLD = 5

# Send email for any change
MIN_CHANGES_THRESHOLD = 1
```

### Select Which Scrapers to Monitor

```python
MONITORED_SCRAPERS = [
    "meinhausshop",
    "pumpe24",
    # Add or remove scrapers as needed
]
```

### Limit Products in Email

```python
# Show max 50 products per section (to avoid huge emails)
MAX_PRODUCTS_IN_EMAIL = 50
```

## Scheduling Daily Notifications

### Windows (Task Scheduler)

1. Open **Task Scheduler**
2. Create **New Task**
3. **Trigger:** Daily at 2:00 AM
4. **Action:** Run program
   - Program: `python`
   - Arguments: `C:\path\to\run_scrapers_with_notifications.py`
   - Start in: `C:\path\to\scrapers`

### Linux/Mac (Cron)

Add to crontab:

```bash
# Run daily at 2:00 AM
0 2 * * * cd /path/to/scrapers && python run_scrapers_with_notifications.py
```

## Troubleshooting

### "Authentication failed" Error

**For Gmail:**
- Make sure you're using an **App Password**, not your regular password
- Enable 2-Step Verification first
- Generate a new App Password specifically for this script

**For Outlook:**
- Use your regular password
- Make sure "Less secure app access" is enabled (if required)

### "Connection refused" Error

- Check your SMTP server and port
- Make sure your firewall isn't blocking port 587
- Try port 465 with SSL instead

### No Email Received

- Check spam/junk folder
- Verify recipient email address is correct
- Run test script to check configuration
- Check email logs in console output

### "No changes detected" Every Time

This is normal for the first run! The system needs a baseline to compare against.

After the first run:
- A snapshot is saved in `data/snapshots/`
- Next run will compare against this snapshot
- Changes will be detected

## Advanced Features

### Multiple Recipients

```python
RECIPIENT_EMAILS = [
    "manager@company.com",
    "team@company.com",
    "alerts@company.com",
]
```

### Custom Email Templates

Edit the `format_html_email()` method in `email_notifier.py` to customize:
- Colors
- Layout
- Additional information
- Company branding

### Webhook Integration

Instead of email, you can modify the code to send to:
- Slack
- Discord
- Microsoft Teams
- Custom webhook

## Files Overview

- **`email_notifier.py`** - Main notification system
- **`email_config.py`** - Your email settings (keep secure!)
- **`run_scrapers_with_notifications.py`** - Run all scrapers + send emails
- **`test_email_notifications.py`** - Test your email setup
- **`data/snapshots/`** - Stores previous data for comparison

## Security Notes

⚠️ **IMPORTANT:**

1. **Never commit `email_config.py` with real passwords to git**
2. Use **App Passwords** for Gmail (more secure)
3. Keep your email credentials secure
4. Add `email_config.py` to `.gitignore`

## Support

If you need help:
1. Run the test script first
2. Check the troubleshooting section
3. Review console output for error messages
4. Verify email configuration is correct

## Example Email Output

```
📊 Scraper Update Report: MEINHAUSSHOP

Date: 2026-01-29 14:30:00

Summary:
• New Products: 15
• Updated Products: 8
• Removed Products: 2

🆕 New Products
[Table with product details]

🔄 Updated Products
[Table showing what changed]

❌ Removed Products
[Table of removed items]
```

---

**Ready to start?** Run the test script first:

```bash
python test_email_notifications.py
```
