@echo off
echo ========================================
echo Testing Production Script Locally
echo ========================================
echo.
echo This will run the production script with NO LIMITS
echo It will scrape ALL products from all 9 websites
echo.
echo Press Ctrl+C to cancel, or
pause

python run_production_powerbi.py

echo.
echo ========================================
echo Test Complete
echo ========================================
pause
