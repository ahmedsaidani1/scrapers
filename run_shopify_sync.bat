@echo off
echo ========================================
echo  WEEKLY SHOPIFY SYNC
echo ========================================
echo.
echo Syncing products to Shopify...
cd /d "C:\Users\ahmed\Desktop\scrapers"
python shopify_api_integration.py
echo.
echo ========================================
echo  SHOPIFY SYNC COMPLETE
echo ========================================
pause
