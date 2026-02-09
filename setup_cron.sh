#!/bin/bash
# ============================================================================
# Setup cron job for nightly scraper execution
# Run this script once to configure automated nightly runs
# ============================================================================

echo "=========================================="
echo "Cron Job Setup for Web Scrapers"
echo "=========================================="

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Project directory: $PROJECT_DIR"

# Path to the run script
RUN_SCRIPT="$PROJECT_DIR/run_all_scrapers.sh"

# Make sure the run script is executable
chmod +x "$RUN_SCRIPT"
echo "✓ Made run_all_scrapers.sh executable"

# Create logs directory for cron output
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/cron_logs"

# Create a cron job entry
# This runs at midnight (00:00) every Sunday (weekly)
CRON_ENTRY="0 0 * * 0 cd $PROJECT_DIR && $RUN_SCRIPT >> $PROJECT_DIR/cron_logs/cron_\$(date +\%Y\%m\%d).log 2>&1"

echo ""
echo "Proposed cron job:"
echo "$CRON_ENTRY"
echo ""
echo "This will run the scrapers every Sunday at midnight (00:00)"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "run_all_scrapers.sh"; then
    echo "⚠ Cron job already exists!"
    echo ""
    echo "Current crontab:"
    crontab -l | grep "run_all_scrapers.sh"
    echo ""
    read -p "Do you want to replace it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled. No changes made."
        exit 0
    fi
    # Remove old entry
    crontab -l | grep -v "run_all_scrapers.sh" | crontab -
fi

# Add the new cron job
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "✓ Cron job installed successfully!"
echo ""
echo "Verification:"
echo "-------------"
crontab -l | grep "run_all_scrapers.sh"
echo ""
echo "Commands:"
echo "---------"
echo "View all cron jobs:    crontab -l"
echo "Edit cron jobs:        crontab -e"
echo "Remove all cron jobs:  crontab -r"
echo ""
echo "=========================================="
echo "Cron Schedule Options:"
echo "=========================================="
echo "Every Sunday at midnight: 0 0 * * 0"
echo "Every Monday at midnight: 0 0 * * 1"
echo "Every Sunday at 2 AM:     0 2 * * 0"
echo "Every Sunday at 3 AM:     0 3 * * 0"
echo "Twice weekly (Sun, Wed):  0 0 * * 0,3"
echo "Every night at midnight:  0 0 * * *"
echo ""
echo "To change the schedule:"
echo "1. Edit this script (setup_cron.sh)"
echo "2. Change the CRON_ENTRY line"
echo "3. Run this script again"
echo "=========================================="
echo ""
echo "Logs will be saved to: $PROJECT_DIR/cron_logs/"
echo "=========================================="
