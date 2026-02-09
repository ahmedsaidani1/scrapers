# Weekly Automation Setup - Sunday 00:00
# Run this script as Administrator

$scriptPath = (Get-Location).Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  WEEKLY AUTOMATION SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "Setting up complete weekly automation..." -ForegroundColor Green
Write-Host "Schedule: Every Sunday at 00:00 (Midnight)" -ForegroundColor Yellow
Write-Host ""

# ============================================
# COMPLETE AUTOMATION TASK
# Sunday 00:00 (Midnight)
# ============================================

Write-Host "Creating task: Weekly_Complete_Automation" -ForegroundColor Yellow
Write-Host ""
Write-Host "This task will:" -ForegroundColor Gray
Write-Host "  1. Scrape all websites" -ForegroundColor Gray
Write-Host "  2. Detect changes (new/updated products)" -ForegroundColor Gray
Write-Host "  3. Send email notifications" -ForegroundColor Gray
Write-Host "  4. Update Google Sheets" -ForegroundColor Gray
Write-Host "  5. Generate Shopify CSV files" -ForegroundColor Gray
Write-Host "  6. Upload to Shopify (only changed products)" -ForegroundColor Gray
Write-Host ""

# Delete existing task if it exists
schtasks /delete /tn "Weekly_Complete_Automation" /f 2>$null

# Create batch file
$batchContent = @"
@echo off
echo ========================================
echo  WEEKLY COMPLETE AUTOMATION
echo ========================================
echo.
echo Start time: %date% %time%
echo.
cd /d "$scriptPath"
python run_complete_automation.py
echo.
echo End time: %date% %time%
echo.
echo ========================================
echo  AUTOMATION COMPLETE
echo ========================================
echo.
echo Check your email at pumpen@solarics.de for notifications
echo.
pause
"@

$batchFile = "$scriptPath\run_weekly_complete.bat"
$batchContent | Out-File -FilePath $batchFile -Encoding ASCII

Write-Host "Created batch file: $batchFile" -ForegroundColor Gray
Write-Host ""

# Create the scheduled task
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$batchFile`"" -WorkingDirectory $scriptPath
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "00:00"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 12)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

try {
    Register-ScheduledTask -TaskName "Weekly_Complete_Automation" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Complete weekly automation: Scrape, detect changes, email notifications, Google Sheets, Shopify upload" `
        -Force | Out-Null
    
    Write-Host "✓ Task created successfully!" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to create task: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Display schedule
Write-Host "Weekly Schedule:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Every Sunday at 00:00 (Midnight)" -ForegroundColor White
Write-Host "  ├─ 1. Scrape all websites (~2-3 hours)" -ForegroundColor Gray
Write-Host "  ├─ 2. Detect changes (new/updated products)" -ForegroundColor Gray
Write-Host "  ├─ 3. Send email notifications to pumpen@solarics.de" -ForegroundColor Gray
Write-Host "  ├─ 4. Update Google Sheets (~30 min)" -ForegroundColor Gray
Write-Host "  ├─ 5. Generate Shopify CSV files" -ForegroundColor Gray
Write-Host "  └─ 6. Upload to Shopify (only changed products) (~1-2 hours)" -ForegroundColor Gray
Write-Host ""
Write-Host "  Total estimated time: 4-6 hours" -ForegroundColor Cyan
Write-Host ""

# Verify task
Write-Host "Verifying task..." -ForegroundColor Yellow
Write-Host ""

$task = Get-ScheduledTask -TaskName "Weekly_Complete_Automation" -ErrorAction SilentlyContinue

if ($task) {
    Write-Host "✓ Weekly_Complete_Automation" -ForegroundColor Green
    Write-Host "  Status: $($task.State)" -ForegroundColor Gray
    Write-Host "  Next run: $($task.Triggers[0].StartBoundary)" -ForegroundColor Gray
    Write-Host "  User: $($task.Principal.UserId)" -ForegroundColor Gray
} else {
    Write-Host "✗ Weekly_Complete_Automation - NOT FOUND" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURATION SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Email Notifications:" -ForegroundColor Yellow
Write-Host "  Sender: pumpen@solarics.de" -ForegroundColor White
Write-Host "  Recipient: pumpen@solarics.de" -ForegroundColor White
Write-Host "  SMTP: smtp-mail.outlook.com" -ForegroundColor White
Write-Host ""
Write-Host "Google Sheets:" -ForegroundColor Yellow
Write-Host "  Configured for all scrapers" -ForegroundColor White
Write-Host "  Using credentials.json" -ForegroundColor White
Write-Host ""
Write-Host "Shopify:" -ForegroundColor Yellow
Write-Host "  Only uploads new/updated products" -ForegroundColor White
Write-Host "  20% markup applied" -ForegroundColor White
Write-Host "  Duplicate detection enabled" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MANUAL COMMANDS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View task details:" -ForegroundColor Yellow
Write-Host "  schtasks /query /tn `"Weekly_Complete_Automation`" /fo LIST /v" -ForegroundColor White
Write-Host ""
Write-Host "Run task manually (for testing):" -ForegroundColor Yellow
Write-Host "  schtasks /run /tn `"Weekly_Complete_Automation`"" -ForegroundColor White
Write-Host ""
Write-Host "Or run directly:" -ForegroundColor Yellow
Write-Host "  python run_complete_automation.py" -ForegroundColor White
Write-Host "  python run_complete_automation.py 50  # Test with 50 products" -ForegroundColor White
Write-Host ""
Write-Host "Delete task:" -ForegroundColor Yellow
Write-Host "  schtasks /delete /tn `"Weekly_Complete_Automation`" /f" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  READY FOR PRODUCTION!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The automation will run every Sunday at midnight." -ForegroundColor White
Write-Host "You will receive email notifications for any changes." -ForegroundColor White
Write-Host "No human intervention required!" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
