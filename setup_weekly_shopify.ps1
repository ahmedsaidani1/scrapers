# Setup Weekly Shopify Sync Task
# Run as Administrator

param(
    [Parameter(Mandatory=$true)]
    [string]$Email,
    
    [Parameter(Mandatory=$true)]
    [string]$Password,
    
    [int]$Markup = 20,
    [int]$DelayHours = 2
)

$TaskName = "Weekly_Shopify_Sync"
$ScriptPath = Join-Path $PSScriptRoot "weekly_shopify_sync.py"

# Remove old task
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create action
$Action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "`"$ScriptPath`" `"$Email`" `"$Password`" $Markup" `
    -WorkingDirectory $PSScriptRoot

# Create trigger (Sunday at 4 AM - 2 hours after scrapers)
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "04:00"

# Settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Register
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Weekly Shopify sync (no API)" `
    -User $env:USERNAME `
    -RunLevel Highest

Write-Host "✓ Task created: $TaskName" -ForegroundColor Green
Write-Host "  Schedule: Every Sunday at 04:00" -ForegroundColor Cyan
Write-Host "  Markup: $Markup%" -ForegroundColor Cyan
Write-Host "`nTo test now:" -ForegroundColor Yellow
Write-Host "  python weekly_shopify_sync.py `"$Email`" `"$Password`" $Markup"
