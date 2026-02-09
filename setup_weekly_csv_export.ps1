# Setup weekly CSV export automation
# NO SHOPIFY CREDENTIALS NEEDED

param([int]$Markup = 20)

$TaskName = "Weekly_Shopify_CSV_Export"
$ScriptPath = Join-Path $PSScriptRoot "shopify_csv_export.py"

# Remove old task
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create action
$Action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "`"$ScriptPath`" $Markup" `
    -WorkingDirectory $PSScriptRoot

# Trigger: Sunday at 4 AM (2 hours after scrapers)
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "04:00"

# Settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

# Register
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Weekly Shopify CSV export" `
    -User $env:USERNAME `
    -RunLevel Highest

Write-Host "=" * 70 -ForegroundColor Green
Write-Host "AUTOMATION SETUP COMPLETE" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "`nTask: $TaskName"
Write-Host "Schedule: Every Sunday at 04:00"
Write-Host "Markup: $Markup%"
Write-Host "Output: shopify_imports/ folder"
Write-Host "`n" + "=" * 70
Write-Host "WHAT HAPPENS WEEKLY:" -ForegroundColor Cyan
Write-Host "=" * 70
Write-Host "Sunday 2:00 AM - Scrapers run"
Write-Host "Sunday 4:00 AM - CSV files generated automatically"
Write-Host "               - Files saved to shopify_imports/"
Write-Host "`n" + "=" * 70
Write-Host "FOR YOUR CLIENT:" -ForegroundColor Yellow
Write-Host "=" * 70
Write-Host "`nOption 1: Matrixify App (Recommended)"
Write-Host "  - Install from Shopify App Store ($30/month)"
Write-Host "  - You upload CSVs to Dropbox/Google Drive"
Write-Host "  - Matrixify imports from URL weekly"
Write-Host "`nOption 2: Manual Import"
Write-Host "  - You send them the CSV files weekly"
Write-Host "  - They import via Shopify Admin"
Write-Host "`nOption 3: Shopify Flow (Shopify Plus only)"
Write-Host "  - Automated import workflows"
Write-Host "`n" + "=" * 70
Write-Host "CSV files ready in: shopify_imports/" -ForegroundColor Green
Write-Host "=" * 70
