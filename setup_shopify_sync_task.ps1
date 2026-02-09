# Setup Windows Task for Shopify sync (runs AFTER scrapers)
# Run this script as Administrator

param(
    [Parameter(Mandatory=$true)]
    [string]$ShopifyEmail,
    
    [Parameter(Mandatory=$true)]
    [string]$ShopifyPassword,
    
    [Parameter(Mandatory=$false)]
    [int]$DelayHours = 2  # Hours after scraper task starts
)

Write-Host "=" * 70
Write-Host "SETTING UP SHOPIFY SYNC TASK"
Write-Host "=" * 70

$ScriptDir = $PSScriptRoot
$PythonScript = Join-Path $ScriptDir "shopify_sync_from_sheets.py"

# Check if script exists
if (-not (Test-Path $PythonScript)) {
    Write-Host "Error: shopify_sync_from_sheets.py not found!" -ForegroundColor Red
    exit 1
}

# Task name
$TaskName = "Shopify_Sync_After_Scrapers"

# Remove existing task
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "`nRemoving existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create action
$Action = New-ScheduledTaskAction -Execute "python" `
    -Argument "`"$PythonScript`" `"$ShopifyEmail`" `"$ShopifyPassword`" 20" `
    -WorkingDirectory $ScriptDir

# Create trigger (same schedule as scrapers + delay)
# Assuming scrapers run Sunday at 2 AM, this runs Sunday at 4 AM (2 hour delay)
$TriggerTime = (Get-Date "2:00 AM").AddHours($DelayHours)
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At $TriggerTime

# Settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Register task
Write-Host "`nRegistering scheduled task..." -ForegroundColor Cyan

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Sync Google Sheets data to Shopify (runs after scrapers)" `
    -User $env:USERNAME `
    -RunLevel Highest

Write-Host "`n" + "=" * 70
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "=" * 70

Write-Host "`nTask Details:"
Write-Host "  Name: $TaskName"
Write-Host "  Schedule: Every Sunday at $($TriggerTime.ToString('HH:mm'))"
Write-Host "  Delay: $DelayHours hours after scrapers start"
Write-Host "  Script: $PythonScript"

Write-Host "`nWorkflow:"
Write-Host "  1. Scrapers run (your existing task)"
Write-Host "  2. Wait $DelayHours hours for scrapers to finish"
Write-Host "  3. This task runs:"
Write-Host "     - Downloads data from Google Sheets"
Write-Host "     - Converts to Shopify CSV (20% markup)"
Write-Host "     - Uploads to Shopify automatically"

Write-Host "`nTo test now:"
Write-Host "  python shopify_sync_from_sheets.py `"$ShopifyEmail`" `"$ShopifyPassword`" 20"

Write-Host "`nTo adjust delay:"
Write-Host "  .\setup_shopify_sync_task.ps1 -ShopifyEmail `"$ShopifyEmail`" -ShopifyPassword `"$ShopifyPassword`" -DelayHours 3"

Write-Host "`n" + "=" * 70
