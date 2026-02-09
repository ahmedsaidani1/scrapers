#!/bin/bash
# ============================================================================
# Run all scrapers in parallel and push to Google Sheets
# Usage: ./run_all_scrapers.sh
# ============================================================================

echo "=========================================="
echo "Running All Scrapers in Parallel"
echo "=========================================="
echo "Start time: $(date)"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run the parallel scraper script
python3 run_all_scrapers_parallel.py

EXIT_CODE=$?

echo ""
echo "=========================================="
echo "All scrapers completed"
echo "End time: $(date)"
echo "Exit code: $EXIT_CODE"
echo "=========================================="

exit $EXIT_CODE
