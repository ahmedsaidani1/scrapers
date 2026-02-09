# Production Schedule Setup for Weekly Automation
# Run this script as Administrator

$scriptPath = "C:\Users\ahmed\Desktop\scrapers"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRODUCTION SCHEDULE SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "Setting up weekly automation schedule..." -ForegroundColor Green
Write-Host ""

# ============================================
# TASK 1: Scrapers + Google Sheets Sync
# Sunday 00:00 (Midnight)
# ============================================

Write-Host "[1/2] Creating task: Weekly_Scrapers_And_Sheets" -ForegroundColor Yellow
Write-Host "      Schedule: Every Sunday at 00:00 (Midnight)" -ForegroundColor Gray
Write-Host "      Duration: ~3-4 hours" -ForegroundColor Gray
Write-Host ""

# Delete existing task if it exists
schtasks /delete /tn "Weekly_Scrapers_And_Sheets" /f 2>$null

# Create batch file to run production automation
$batchContent = @"
@echo off
echo ========================================
echo  WEEKLY AUTOMATION - PRODUCTION RUN
echo ========================================
echo.
echo Running complete production workflow...
echo   1. Scrape all websites
echo   2. Send email notifications
echo   3. Update Google Sheets
echo   4. Generate Shopify CSV files
echo   5. Update Power BI Sheet
echo.
cd /d "$scriptPath"
python run_production.py
echo.
echo ========================================
echo  AUTOMATION COMPLETE
echo ========================================
pause
"@

$batchFile = "$scriptPath\run_weekly_automation.bat"
$batchContent | Out-File -FilePath $batchFile -Encoding ASCII

# Create the scheduled task
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$batchFile`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "00:00"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

try {
    Register-ScheduledTask -TaskName "Weekly_Scrapers_And_Sheets" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Weekly automation: Run all scrapers and sync to Google Sheets" `
        -Force | Out-Null
    
    Write-Host "  ✓ Task created successfully!" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to create task: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# TASK 2: Shopify API Sync
# Sunday 10:00 (10 AM)
# ============================================

Write-Host "[2/2] Creating task: Weekly_Shopify_Sync" -ForegroundColor Yellow
Write-Host "      Schedule: Every Sunday at 10:00 (10 AM)" -ForegroundColor Gray
Write-Host "      Duration: ~5-6 hours" -ForegroundColor Gray
Write-Host ""

# Delete existing task if it exists
schtasks /delete /tn "Weekly_Shopify_Sync" /f 2>$null

# Create batch file for Shopify sync
$shopifyBatchContent = @"
@echo off
echo ========================================
echo  WEEKLY SHOPIFY SYNC
echo ========================================
echo.
echo Syncing products to Shopify...
cd /d "$scriptPath"
python shopify_api_integration.py
echo.
echo ========================================
echo  SHOPIFY SYNC COMPLETE
echo ========================================
pause
"@

$shopifyBatchFile = "$scriptPath\run_shopify_sync.bat"
$shopifyBatchContent | Out-File -FilePath $shopifyBatchFile -Encoding ASCII

# Create the scheduled task
$shopifyAction = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$shopifyBatchFile`""
$shopifyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "10:00"
$shopifySettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable
$shopifyPrincipal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

try {
    Register-ScheduledTask -TaskName "Weekly_Shopify_Sync" `
        -Action $shopifyAction `
        -Trigger $shopifyTrigger `
        -Settings $shopifySettings `
        -Principal $shopifyPrincipal `
        -Description "Weekly automation: Sync products to Shopify (runs 10 hours after scrapers)" `
        -Force | Out-Null
    
    Write-Host "  ✓ Task created successfully!" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to create task: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Display schedule
Write-Host "Weekly Schedule:" -ForegroundColor Yellow
Write-Host "  Sunday 00:00 (Midnight)" -ForegroundColor White
Write-Host "    ├─ Run 18 scrapers (~3 hours)" -ForegroundColor Gray
Write-Host "    ├─ Save to data/*.csv" -ForegroundColor Gray
Write-Host "    ├─ Sync to Google Sheets (~30 min)" -ForegroundColor Gray
Write-Host "    └─ Update Power BI Sheet (~5 min)" -ForegroundColor Gray
Write-Host ""
Write-Host "  Sunday 10:00 (10 AM)" -ForegroundColor White
Write-Host "    ├─ Read data/*.csv" -ForegroundColor Gray
Write-Host "    ├─ Check for duplicates" -ForegroundColor Gray
Write-Host "    ├─ Update prices if changed" -ForegroundColor Gray
Write-Host "    └─ Sync to Shopify (~5-6 hours)" -ForegroundColor Gray
Write-Host ""

# Verify tasks
Write-Host "Verifying tasks..." -ForegroundColor Yellow
Write-Host ""

$task1 = Get-ScheduledTask -TaskName "Weekly_Scrapers_And_Sheets" -ErrorAction SilentlyContinue
$task2 = Get-ScheduledTask -TaskName "Weekly_Shopify_Sync" -ErrorAction SilentlyContinue

if ($task1) {
    Write-Host "  ✓ Weekly_Scrapers_And_Sheets" -ForegroundColor Green
    Write-Host "    Next run: $($task1.Triggers[0].StartBoundary)" -ForegroundColor Gray
} else {
    Write-Host "  ✗ Weekly_Scrapers_And_Sheets - NOT FOUND" -ForegroundColor Red
}

if ($task2) {
    Write-Host "  ✓ Weekly_Shopify_Sync" -ForegroundColor Green
    Write-Host "    Next run: $($task2.Triggers[0].StartBoundary)" -ForegroundColor Gray
} else {
    Write-Host "  ✗ Weekly_Shopify_Sync - NOT FOUND" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MANUAL COMMANDS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View tasks:" -ForegroundColor Yellow
Write-Host "  schtasks /query /tn `"Weekly_Scrapers_And_Sheets`" /fo LIST /v" -ForegroundColor White
Write-Host "  schtasks /query /tn `"Weekly_Shopify_Sync`" /fo LIST /v" -ForegroundColor White
Write-Host ""
Write-Host "Run tasks manually:" -ForegroundColor Yellow
Write-Host "  schtasks /run /tn `"Weekly_Scrapers_And_Sheets`"" -ForegroundColor White
Write-Host "  schtasks /run /tn `"Weekly_Shopify_Sync`"" -ForegroundColor White
Write-Host ""
Write-Host "Delete tasks:" -ForegroundColor Yellow
Write-Host "  schtasks /delete /tn `"Weekly_Scrapers_And_Sheets`" /f" -ForegroundColor White
Write-Host "  schtasks /delete /tn `"Weekly_Shopify_Sync`" /f" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  READY FOR PRODUCTION!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
