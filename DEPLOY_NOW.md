# Deploy to Render - Step by Step (DO THIS NOW)

## 🚀 Let's Deploy This Shit

Follow these steps EXACTLY. Don't skip anything.

---

## STEP 1: Prepare Your Credentials (2 minutes)

### 1.1 Open Your Credentials File
```
Open: credentials/credentials.json
```

### 1.2 Copy ENTIRE Content
- Select ALL text in the file
- Copy it (Ctrl+C)
- Keep it in clipboard - you'll need it soon

**What it looks like:**
```json
{
  "type": "service_account",
  "project_id": "...",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  ...
}
```

✅ Got it copied? Good. Move on.

---

## STEP 2: Push Code to GitHub (5 minutes)

### 2.1 Check What Files You Have
```bash
dir
```

You should see:
- run_production_powerbi.py ✓
- render.yaml ✓
- Procfile ✓
- runtime.txt ✓
- requirements.txt ✓
- All scraper files ✓

### 2.2 Initialize Git (if not already)
```bash
git init
```

### 2.3 Add .gitignore
Make sure credentials.json is NOT committed:

```bash
echo credentials/credentials.json >> .gitignore
echo data/*.csv >> .gitignore
echo logs/*.log >> .gitignore
echo __pycache__/ >> .gitignore
```

### 2.4 Add All Files
```bash
git add .
```

### 2.5 Commit
```bash
git commit -m "Production deployment ready"
```

### 2.6 Create GitHub Repo
1. Go to https://github.com/new
2. Name: `product-scrapers` (or whatever)
3. Make it PRIVATE (important!)
4. Don't initialize with README
5. Click "Create repository"

### 2.7 Push to GitHub
Copy the commands GitHub shows you:
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

✅ Code is on GitHub? Good. Move on.

---

## STEP 3: Create Render Account (2 minutes)

### 3.1 Go to Render
Open: https://render.com/

### 3.2 Sign Up
- Click "Get Started"
- Sign up with GitHub (easiest)
- Authorize Render to access GitHub
- Verify email if needed

✅ Account created? Good. Move on.

---

## STEP 4: Create Cron Job (5 minutes)

### 4.1 Create New Service
1. Click "New +" button (top right)
2. Select "Cron Job"

### 4.2 Connect Repository
1. Click "Connect" next to your repository
2. If you don't see it, click "Configure account"
3. Give Render access to your repo
4. Click "Connect" again

### 4.3 Configure Cron Job

**Name:**
```
powerbi-scraper-production
```

**Environment:**
```
Python 3
```

**Build Command:**
```
pip install -r requirements.txt
```

**Command:**
```
python run_production_powerbi.py
```

**Schedule:**
```
0 2 * * 0
```
(This means: Every Sunday at 2 AM UTC)

**Branch:**
```
main
```

### 4.4 Advanced Settings (Click "Advanced")

**Instance Type:**
```
Free (512 MB RAM, 0.1 CPU)
```

**Auto-Deploy:**
```
Yes (toggle ON)
```

✅ Configured? DON'T click "Create Cron Job" yet. Move on.

---

## STEP 5: Add Environment Variables (CRITICAL!)

### 5.1 Scroll to Environment Variables Section

### 5.2 Add Credentials
Click "Add Environment Variable"

**Key:**
```
GOOGLE_APPLICATION_CREDENTIALS
```

**Value:**
Paste the ENTIRE credentials.json content you copied in Step 1

It should look like:
```json
{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

**IMPORTANT:** Make sure you paste the ENTIRE JSON, including the curly braces!

✅ Credentials added? Good. Move on.

---

## STEP 6: Deploy! (1 minute)

### 6.1 Create Cron Job
Click the big blue button: **"Create Cron Job"**

### 6.2 Wait for Build
- Render will start building
- You'll see logs in real-time
- Wait for "Build successful"
- Takes ~2-3 minutes

**What you'll see:**
```
==> Cloning from https://github.com/...
==> Checking out commit ...
==> Running build command: pip install -r requirements.txt
==> Installing dependencies...
==> Build successful!
```

✅ Build successful? Good. Move on.

---

## STEP 7: Test It NOW (10 minutes)

### 7.1 Trigger Manual Run
1. You're on the Cron Job page
2. Click "Trigger Run" button (top right)
3. Confirm

### 7.2 Watch the Logs
You'll see:
```
================================================================================
PRODUCTION POWER BI DATA PIPELINE
================================================================================
Started: 2026-02-15 14:23:45
Target Sheet ID: 1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg
Mode: PRODUCTION - Scraping ALL products (no limits)
Total scrapers: 9
===================================