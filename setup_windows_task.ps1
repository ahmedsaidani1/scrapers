# ============================================================================
# Setup Windows Task Scheduler for Nightly Scraper Execution
# Run this script in PowerShell as Administrator
# ============================================================================

Write-Host "=========================================="
Write-Host "Windows Task Scheduler Setup"
Write-Host "=========================================="
Write-Host ""

# Get the current directory (where the script is located)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Project directory: $ScriptDir"
Write-Host ""

# Configuration
$TaskName = "WebScrapers-NightlyRun"
$PythonScript = Join-Path $ScriptDir "run_all_scrapers_parallel.py"
$LogDir = Join-Path $ScriptDir "scheduled_logs"

# Create log directory if it doesn't exist
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
    Write-Host "Created log directory: $LogDir"
}

# Find Python executable
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonExe) {
    $PythonExe = (Get-Command python3 -ErrorAction SilentlyContinue).Source
}

if (-not $PythonExe) {
    Write-Host "Python not found in PATH!" -ForegroundColor Red
    Write-Host "Please install Python or add it to your PATH"
    exit 1
}

Write-Host "Found Python: $PythonExe"
Write-Host ""

# Check if task already exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($ExistingTask) {
    Write-Host "Task already exists!" -ForegroundColor Yellow
    Write-Host ""
    $Response = Read-Host "Do you want to replace it? (Y/N)"
    
    if ($Response -ne 'Y' -and $Response -ne 'y') {
        Write-Host "Cancelled. No changes made."
        exit 0
    }
    
    # Remove existing task
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task"
}

Write-Host ""
Write-Host "Creating scheduled task..."
Write-Host "  - Task Name: $TaskName"
Write-Host "  - Schedule: Weekly on Sunday at midnight (00:00)"
Write-Host "  - Script: $PythonScript"
Write-Host ""

# Create the action (what to run)
$ActionArgs = "`"$PythonScript`""
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $ActionArgs -WorkingDirectory $ScriptDir

# Create the trigger (when to run) - Weekly on Sunday at midnight
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "00:00"

# Create settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 6)

# Get current user
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

# Register the task
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Automated weekly web scraping - runs all scrapers every Sunday and pushes to Google Sheets" -ErrorAction Stop | Out-Null
    
    Write-Host "Task created successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Display task info
    Write-Host "=========================================="
    Write-Host "Task Information"
    Write-Host "=========================================="
    Write-Host "Task Name: $TaskName"
    Write-Host "Schedule: Weekly on Sunday at midnight (00:00)"
    Write-Host "Next Run: " -NoNewline
    
    $Task = Get-ScheduledTask -TaskName $TaskName
    $TaskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
    Write-Host $TaskInfo.NextRunTime
    
    Write-Host ""
    Write-Host "=========================================="
    Write-Host "Management Commands"
    Write-Host "=========================================="
    Write-Host "View task:"
    Write-Host "  Get-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "Run task manually:"
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "Disable task:"
    Write-Host "  Disable-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "Enable task:"
    Write-Host "  Enable-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "Remove task:"
    Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "=========================================="
    Write-Host "Schedule Options"
    Write-Host "=========================================="
    Write-Host "To change the schedule, edit this script and modify the trigger line"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host '  Weekly on Sunday:  -Weekly -DaysOfWeek Sunday -At "00:00"'
    Write-Host '  Weekly on Monday:  -Weekly -DaysOfWeek Monday -At "00:00"'
    Write-Host '  Twice weekly:      -Weekly -DaysOfWeek Sunday,Wednesday -At "00:00"'
    Write-Host '  Daily at 2 AM:     -Daily -At "02:00"'
    Write-Host ""
    Write-Host "Then run this script again to update the task."
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "Setup complete! The scrapers will run automatically every Sunday at midnight." -ForegroundColor Green
    
} catch {
    Write-Host "Failed to create task: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure you are running PowerShell as Administrator!"
    exit 1
}
