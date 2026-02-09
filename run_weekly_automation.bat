@echo off
echo ========================================
echo  WEEKLY AUTOMATION - SCRAPERS + SHEETS
echo ========================================
echo.
echo [1/2] Running scrapers...
cd /d "C:\Users\ahmed\Desktop\scrapers"
python run_all_scrapers_sequential.py
echo.
echo [2/2] Syncing to Google Sheets...
python create_sheets.py
echo.
echo ========================================
echo  AUTOMATION COMPLETE
echo ========================================
pause
