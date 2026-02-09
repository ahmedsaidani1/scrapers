@echo off
echo ====================================================================
echo WEEKLY SHOPIFY CSV EXPORT SETUP
echo ====================================================================
echo.
echo This will create a weekly task to generate Shopify CSV files.
echo NO SHOPIFY CREDENTIALS NEEDED.
echo.
pause

powershell -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File setup_weekly_csv_export.ps1 -Markup 20' -Verb RunAs"

echo.
echo ====================================================================
echo SETUP COMPLETE!
echo ====================================================================
echo.
echo CSV files will be generated every Sunday at 4:00 AM
echo Location: shopify_imports/ folder
echo.
echo GIVE THESE FILES TO YOUR CLIENT:
echo   - They can import manually in Shopify Admin
echo   - Or use Matrixify app for automation
echo.
pause
