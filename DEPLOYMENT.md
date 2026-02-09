# Deployment Guide - Automated Nightly Scraping

Complete guide for deploying the scraping system to a Linux server with automated nightly runs.

## Quick Start

```bash
# 1. Upload files to server
scp -r * user@server:/path/to/scrapers/

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Setup cron job
./setup_cron.sh
```

Done! Scrapers will run automatically at 2 AM every night.

---

## Detailed Deployment Steps

### 1. Server Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum (4GB+ recommended for parallel execution)
- **Disk**: 10GB free space
- **Network**: Stable internet connection

### 2. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install Git (if cloning from repository)
sudo apt install git -y

# Verify installations
python3 --version
pip3 --version
```

### 3. Upload Project Files

**Option A: Using SCP**
```bash
# From your local machine
scp -r /path/to/scrapers user@server:/home/user/scrapers
```

**Option B: Using Git**
```bash
# On the server
git clone <your-repo-url>
cd scrapers
```

**Option C: Using rsync (recommended for updates)**
```bash
# From your local machine
rsync -avz --exclude 'data/' --exclude 'logs/' \
  /path/to/scrapers/ user@server:/home/user/scrapers/
```

### 4. Install Python Dependencies

```bash
cd /path/to/scrapers

# Install all required packages
pip3 install -r requirements.txt

# Verify installation
python3 -c "import requests, bs4, gspread; print('All packages installed')"
```

### 5. Configure Google Sheets Access

**Upload credentials:**
```bash
# From local machine
scp credentials.json user@server:/path/to/scrapers/credentials/

# On server, set proper permissions
chmod 600 credentials/credentials.json
chmod 700 credentials/
```

**Verify Sheet IDs in config.py:**
```python
SHEET_IDS = {
    "meinhausshop": "1KaMWOGh9KEPvvxWQRKLu-fLr0-aSLdhn5IbdZ0XyvTQ",
    "heima24": "1nfHVN4RZM-tED-HtXUWV7bwtAWjctih7dJ2eOyTRj08",
    # ... etc
}
```

**Ensure service account has access:**
- Service account: `webscraping-solarics@webscrapingmajd2.iam.gserviceaccount.com`
- Must have "Editor" access to all Google Sheets

### 6. Test the System

```bash
# Test a single scraper
python3 meinhausshop_scraper.py

# Test parallel execution (all scrapers)
python3 run_all_scrapers_parallel.py

# Check output
ls -lh data/
head data/meinhausshop.csv
```

### 7. Setup Automated Nightly Runs

```bash
# Make scripts executable
chmod +x setup_cron.sh
chmod +x run_all_scrapers.sh

# Run the cron setup script
./setup_cron.sh

# Verify cron job is installed
crontab -l
```

You should see:
```
0 0 * * * cd /path/to/scrapers && ./run_all_scrapers.sh >> /path/to/scrapers/cron_logs/cron_$(date +%Y%m%d).log 2>&1
```

### 8. Verify Everything Works

```bash
# Check cron service is running
sudo systemctl status cron

# Wait for first automated run (2 AM) or trigger manually
./run_all_scrapers.sh

# Check logs
tail -f cron_logs/cron_$(date +%Y%m%d).log
tail -f logs/meinhausshop.log

# Verify Google Sheets are updated
# Visit: https://docs.google.com/spreadsheets/d/1KaMWOGh9KEPvvxWQRKLu-fLr0-aSLdhn5IbdZ0XyvTQ
```

---

## What Runs Automatically

The cron job executes `run_all_scrapers_parallel.py` every night at midnight (00:00):

### Scrapers Included:
1. **meinhausshop.de** - ~169,000 products (Shopware)
2. **heima24.de** - ~24,500 products (Custom platform)
3. **sanundo.de** - ~21,200 products (Shopware)
4. **heizungsdiscount24.de** - ~68,300 products (JTL-Shop)
5. **wolfonlineshop.de** - ~160 products (Shopware 6)
6. **st-shop24.de** - ~243 products (Magento)
7. **selfio.de** - Shopware 6 with compressed sitemaps
8. **pumpe24.de** - ~46 products (Cloudflare bypass)
9. **wasserpumpe.de** - ~49 products (Cloudflare bypass)

### Execution Flow:
1. All 9 scrapers run in parallel (simultaneous execution)
2. Each scraper saves data to `data/<scraper_name>.csv`
3. Data is automatically pushed to corresponding Google Sheet
4. Logs saved to `logs/<scraper_name>.log`
5. Cron execution log saved to `cron_logs/cron_YYYYMMDD.log`

---

## Configuration

### Change Schedule

Edit `setup_cron.sh` and modify the `CRON_ENTRY` line:

```bash
# Default: Every night at midnight
CRON_ENTRY="0 0 * * * ..."

# Other options:
# Every night at 2 AM:    0 2 * * *
# Every night at 3 AM:    0 3 * * *
# Twice daily (12AM, 12PM): 0 0,12 * * *
# Every 6 hours:          0 */6 * * *
# Every Monday at midnight: 0 0 * * 1
# Every hour:             0 * * * *
```

Then run `./setup_cron.sh` again to update.

### Adjust Scraping Behavior

Edit `config.py`:

```python
# Rate limiting (be respectful to websites)
MIN_DELAY = 1  # seconds between requests
MAX_DELAY = 3

# Request timeout
REQUEST_TIMEOUT = 30  # seconds

# Max retries on failure
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries
```

### Switch to Sequential Execution

If server has limited RAM, use sequential instead of parallel:

Edit `run_all_scrapers.sh`:
```bash
# Change this line:
python3 run_all_scrapers_parallel.py

# To:
python3 run_all_scrapers_sequential.py
```

---

## Monitoring & Maintenance

### View Logs

```bash
# Today's cron execution log
tail -f cron_logs/cron_$(date +%Y%m%d).log

# Individual scraper logs
tail -f logs/meinhausshop.log
tail -f logs/pumpe24.log

# View all recent errors
grep ERROR logs/*.log

# View all warnings
grep WARNING logs/*.log
```

### Check Data Files

```bash
# List all CSV files with sizes
ls -lh data/

# Count products in each file
wc -l data/*.csv

# View latest data
head -20 data/meinhausshop.csv
tail -20 data/meinhausshop.csv
```

### Monitor System Resources

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep python

# Monitor in real-time
htop
```

### Verify Google Sheets

Check that sheets are being updated:
- meinhausshop: https://docs.google.com/spreadsheets/d/1KaMWOGh9KEPvvxWQRKLu-fLr0-aSLdhn5IbdZ0XyvTQ
- heima24: https://docs.google.com/spreadsheets/d/1nfHVN4RZM-tED-HtXUWV7bwtAWjctih7dJ2eOyTRj08
- (See `config.py` for all Sheet IDs)

---

## Troubleshooting

### Cron Job Not Running

**Check cron service:**
```bash
sudo systemctl status cron
sudo systemctl start cron  # if stopped
sudo systemctl enable cron  # enable on boot
```

**Verify cron job exists:**
```bash
crontab -l
```

**Check system cron logs:**
```bash
grep CRON /var/log/syslog | tail -20
```

**Test manually:**
```bash
./run_all_scrapers.sh
```

### Google Sheets Push Failing

**Check credentials file:**
```bash
ls -l credentials/credentials.json
cat credentials/credentials.json  # verify it's valid JSON
```

**Verify service account access:**
- Go to each Google Sheet
- Click "Share"
- Ensure `webscraping-solarics@webscrapingmajd2.iam.gserviceaccount.com` has Editor access

**Test manually:**
```bash
python3 -c "from google_sheets_helper import push_data; from config import SHEET_IDS; print('Testing...'); push_data(SHEET_IDS['meinhausshop'], 'data/meinhausshop.csv')"
```

### Scraper Failures

**Check individual logs:**
```bash
tail -100 logs/meinhausshop.log
```

**Test scraper manually:**
```bash
python3 meinhausshop_scraper.py
```

**Common issues:**
- Website structure changed → Update selectors in scraper
- Rate limiting/blocking → Adjust delays in `config.py`
- Network timeout → Increase `REQUEST_TIMEOUT` in `config.py`

### Memory Issues

**Check memory usage:**
```bash
free -h
```

**If running out of memory:**

1. Use sequential execution instead of parallel
2. Add swap space:
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Permission Errors

**Fix script permissions:**
```bash
chmod +x run_all_scrapers.sh
chmod +x setup_cron.sh
```

**Fix credentials permissions:**
```bash
chmod 600 credentials/credentials.json
chmod 700 credentials/
```

**Fix directory permissions:**
```bash
chmod 755 data/ logs/ cron_logs/
```

---

## Security Best Practices

### Protect Credentials

```bash
# Restrict access to credentials
chmod 600 credentials/credentials.json
chmod 700 credentials/

# Verify
ls -la credentials/
```

### Firewall Configuration

```bash
# Enable firewall
sudo ufw enable

# Allow SSH only
sudo ufw allow 22/tcp

# Check status
sudo ufw status
```

### Regular Updates

```bash
# System updates (monthly)
sudo apt update && sudo apt upgrade -y

# Python package updates (quarterly)
pip3 install --upgrade -r requirements.txt
```

### Backup Credentials

```bash
# Backup to secure location
cp credentials/credentials.json ~/backups/credentials_$(date +%Y%m%d).json
chmod 600 ~/backups/credentials_*.json
```

---

## Backup & Recovery

### Manual Backup

```bash
# Backup data files
tar -czf backup_data_$(date +%Y%m%d).tar.gz data/

# Backup logs
tar -czf backup_logs_$(date +%Y%m%d).tar.gz logs/

# Backup credentials
tar -czf backup_credentials_$(date +%Y%m%d).tar.gz credentials/

# Backup everything
tar -czf backup_full_$(date +%Y%m%d).tar.gz \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  .
```

### Automated Weekly Backup

Add to crontab:
```bash
crontab -e

# Add this line (runs every Sunday at 1 AM):
0 1 * * 0 tar -czf /backups/scrapers_$(date +\%Y\%m\%d).tar.gz /path/to/scrapers/data/
```

### Restore from Backup

```bash
# Extract backup
tar -xzf backup_data_20260127.tar.gz

# Verify
ls -lh data/
```

---

## Maintenance Schedule

### Daily (Automatic)
- ✓ Scrapers run at 2 AM
- ✓ Data pushed to Google Sheets
- ✓ Logs saved automatically

### Weekly
- Review error logs: `grep ERROR logs/*.log`
- Check disk space: `df -h`
- Verify Google Sheets are updating
- Review scraper performance

### Monthly
- Update system packages: `sudo apt update && sudo apt upgrade`
- Clean old logs (keep last 30 days)
- Review and optimize scrapers
- Check for website changes

### Quarterly
- Update Python packages: `pip3 install --upgrade -r requirements.txt`
- Review security settings
- Backup credentials
- Performance audit

### Clean Old Logs

```bash
# Remove logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete
find cron_logs/ -name "*.log" -mtime +30 -delete

# Or keep only last 10 files
cd logs/
ls -t *.log | tail -n +11 | xargs rm -f
```

---

## Performance Optimization

### Parallel vs Sequential

**Parallel (default):**
- Faster (all scrapers run simultaneously)
- Higher memory usage
- Recommended for servers with 4GB+ RAM

**Sequential:**
- Slower (scrapers run one at a time)
- Lower memory usage
- Recommended for servers with <4GB RAM

To switch: Edit `run_all_scrapers.sh`

### Adjust Concurrency

Edit `run_all_scrapers_parallel.py`:
```python
# Limit number of parallel processes
num_processes = min(4, len(scrapers))  # Max 4 at a time
```

### Rate Limiting

Edit `config.py`:
```python
# Faster (but more aggressive)
MIN_DELAY = 0.5
MAX_DELAY = 1

# Slower (but more respectful)
MIN_DELAY = 2
MAX_DELAY = 5
```

---

## Support & Documentation

### Key Files
- `CRON_SETUP.md` - Detailed cron documentation
- `QUICKSTART.md` - Quick start guide
- `TECHNICAL_REPORT.md` - Complete technical documentation
- `config.py` - All configuration settings

### Useful Commands

```bash
# View cron jobs
crontab -l

# Edit cron jobs
crontab -e

# Remove all cron jobs
crontab -r

# Test scraper manually
python3 meinhausshop_scraper.py

# Run all scrapers manually
./run_all_scrapers.sh

# Check logs
tail -f logs/meinhausshop.log

# Monitor system
htop
```

### Getting Help

1. Check logs in `logs/` and `cron_logs/`
2. Review error messages
3. Test scrapers manually
4. Verify Google Sheets access
5. Check system resources

---

## Summary

Your scraping system is now deployed and will:
- ✓ Run automatically every night at midnight (00:00)
- ✓ Scrape all 9 websites in parallel
- ✓ Push data to Google Sheets automatically
- ✓ Log all activity for monitoring
- ✓ Continue running even if you log out

No manual intervention required - just monitor logs occasionally and ensure Google Sheets are updating correctly.
