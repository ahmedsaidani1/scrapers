@echo off
echo ====================================================================
echo SHOPIFY AUTOMATION SETUP
echo ====================================================================
echo.
echo This will set up weekly automatic Shopify uploads.
echo NO API NEEDED - uses browser automation.
echo.

set /p email="Enter Shopify Admin Email: "
set /p password="Enter Shopify Admin Password: "
set /p markup="Price Markup %% (default 20): "

if "%markup%"=="" set markup=20

echo.
echo Creating Windows scheduled task...
powershell -ExecutionPolicy Bypass -File setup_weekly_shopify.ps1 -Email "%email%" -Password "%password%" -Markup %markup%

echo.
echo ====================================================================
echo SETUP COMPLETE!
echo ====================================================================
echo.
echo Task: Weekly_Shopify_Sync
echo Schedule: Every Sunday at 4:00 AM
echo Markup: %markup%%%
echo.
echo To test now:
echo   python weekly_shopify_sync.py "%email%" "%password%" %markup%
echo.
pause
