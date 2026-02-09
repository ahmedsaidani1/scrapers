# Automated Weekly Scraper Setup (Cron Job)

This guide explains how to set up the scrapers to run automatically every week.

## Quick Setup (Linux/Mac)

1. Make the setup script executable:
```bash
chmod +x setup_cron.sh
```

2. Run the setup script:
```bash
./setup_cron.sh
```

3. Done! The scrapers will now run automatically every Sunday at midnight (00:00).

## What Gets Installed

The cron job will:
- Run all scrapers in parallel every Sunday at midnight (00:00)
- Automatically push all scraped data to Google Sheets
- Save logs to `cron_logs/` directory
- Continue running even if you log out

## Verify Installation

Check that the cron job is installed:
```bash
crontab -l
```

You should see a line like:
```
0 0 * * 0 cd /path/to/scrapers && ./run_all_scrapers.sh >> /path/to/scrapers/cron_logs/cron_$(date +%Y%m%d).log 2>&1
```

## Change Schedule

To run at a different time, edit `setup_cron.sh` and change this line:
```bash
CRON_ENTRY="0 0 * * 0 ..."
```

Common schedules:
- `0 0 * * 0` - Every Sunday at midnight
- `0 0 * * 1` - Every Monday at midnight
- `0 2 * * 0` - Every Sunday at 2:00 AM
- `0 0 * * 0,3` - Twice weekly (Sunday and Wednesday)
- `0 0 * * *` - Every night at midnight
- `0 2 * * *` - Every night at 2:00 AM

Then run `./setup_cron.sh` again.

## View Logs

Cron execution logs are saved to:
```
cron_logs/cron_YYYYMMDD.log
```

Individual scraper logs are in:
```
logs/
```

## Manual Test

Test the script manually before setting up cron:
```bash
./run_all_scrapers.sh
```

## Remove Cron Job

To stop automatic runs:
```bash
crontab -e
```

Then delete the line containing `run_all_scrapers.sh` and save.

Or remove all cron jobs:
```bash
crontab -r
```

## Troubleshooting

### Cron job not running?

1. Check cron service is running:
```bash
sudo systemctl status cron
```

2. Check system logs:
```bash
grep CRON /var/log/syslog
```

3. Make sure Python and dependencies are in PATH:
```bash
which python3
```

### Permission errors?

Make scripts executable:
```bash
chmod +x run_all_scrapers.sh
chmod +x setup_cron.sh
```

### Google Sheets authentication?

Make sure `credentials/credentials.json` is present and the service account has access to all sheets.

## Windows Alternative

Windows doesn't use cron. Use Task Scheduler instead - see `WINDOWS_SETUP.md` or run:

```powershell
.\setup_windows_task.ps1
```

This will create a scheduled task that runs every Sunday at midnight.
