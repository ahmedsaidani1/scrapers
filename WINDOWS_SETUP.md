# Windows Automated Setup - Task Scheduler

Complete guide for setting up automated weekly scraping on Windows using Task Scheduler.

## Quick Setup

1. **Open PowerShell as Administrator**
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

2. **Navigate to project directory**
   ```powershell
   cd C:\path\to\scrapers
   ```

3. **Run the setup script**
   ```powershell
   .\setup_windows_task.ps1
   ```

4. **Done!** The scrapers will run automatically every Sunday at midnight.

---

## Detailed Setup Instructions

### Prerequisites

- Windows 10 or Windows 11
- Python 3.8+ installed
- Administrator access
- All dependencies installed (`pip install -r requirements.txt`)

### Step 1: Enable PowerShell Script Execution

If you get an error about script execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Run Setup Script

```powershell
# Navigate to project folder
cd C:\Users\ahmed\Desktop\scrapers

# Run setup
.\setup_windows_task.ps1
```

The script will:
- ✓ Find your Python installation
- ✓ Create a scheduled task
- ✓ Set it to run weekly on Sunday at midnight
- ✓ Configure proper permissions

### Step 3: Verify Task Creation

Open Task Scheduler:
- Press `Win + R`
- Type `taskschd.msc`
- Press Enter

Look for task named: **WebScrapers-NightlyRun**

---

## Manual Setup (Alternative Method)

If you prefer to set up manually:

### 1. Open Task Scheduler
- Press `Win + R`
- Type `taskschd.msc`
- Press Enter

### 2. Create Basic Task
- Click "Create Basic Task" in the right panel
- Name: `WebScrapers-NightlyRun`
- Description: `Automated weekly web scraping`
- Click Next

### 3. Set Trigger
- Select "Daily"
- Click Next
- Start: Today's date
- Time: `00:00:00` (midnight)
- Recur every: `1` days
- Click Next

### 4. Set Action
- Select "Start a program"
- Click Next
- Program/script: `python` (or full path like `C:\Python312\python.exe`)
- Add arguments: `run_all_scrapers_parallel.py`
- Start in: `C:\Users\ahmed\Desktop\scrapers` (your project folder)
- Click Next

### 5. Finish
- Check "Open the Properties dialog"
- Click Finish

### 6. Configure Advanced Settings
In the Properties dialog:

**General Tab:**
- ✓ Run whether user is logged on or not
- ✓ Run with highest privileges

**Triggers Tab:**
- Edit trigger if needed

**Actions Tab:**
- Verify action is correct

**Conditions Tab:**
- ✓ Start only if the following network connection is available: Any connection
- ✓ Wake the computer to run this task (optional)

**Settings Tab:**
- ✓ Allow task to be run on demand
- ✓ Run task as soon as possible after a scheduled start is missed
- ✓ If the task fails, restart every: 10 minutes
- ✓ Attempt to restart up to: 3 times
- Stop the task if it runs longer than: 6 hours

Click OK and enter your Windows password if prompted.

---

## Managing the Scheduled Task

### View Task Status

```powershell
Get-ScheduledTask -TaskName "WebScrapers-NightlyRun"
```

### Run Task Manually (Test)

```powershell
Start-ScheduledTask -TaskName "WebScrapers-NightlyRun"
```

Or in Task Scheduler:
- Right-click the task
- Select "Run"

### View Task History

In Task Scheduler:
- Select the task
- Click "History" tab at the bottom
- View all execution logs

### Disable Task

```powershell
Disable-ScheduledTask -TaskName "WebScrapers-NightlyRun"
```

Or in Task Scheduler:
- Right-click the task
- Select "Disable"

### Enable Task

```powershell
Enable-ScheduledTask -TaskName "WebScrapers-NightlyRun"
```

### Remove Task

```powershell
Unregister-ScheduledTask -TaskName "WebScrapers-NightlyRun" -Confirm:$false
```

Or in Task Scheduler:
- Right-click the task
- Select "Delete"

---

## Change Schedule

### Edit the PowerShell Script

Open `setup_windows_task.ps1` and modify this line:

```powershell
$Trigger = New-ScheduledTaskTrigger -Daily -At "00:00"
```

### Schedule Examples

**Daily at 2 AM:**
```powershell
$Trigger = New-ScheduledTaskTrigger -Daily -At "02:00"
```

**Daily at 3 AM:**
```powershell
$Trigger = New-ScheduledTaskTrigger -Daily -At "03:00"
```

**Twice daily (midnight and noon):**
```powershell
$Trigger1 = New-ScheduledTaskTrigger -Daily -At "00:00"
$Trigger2 = New-ScheduledTaskTrigger -Daily -At "12:00"
$Trigger = @($Trigger1, $Trigger2)
```

**Weekly on Monday at midnight:**
```powershell
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "00:00"
```

**Every 6 hours:**
```powershell
$Trigger = New-ScheduledTaskTrigger -Once -At "00:00" -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 365)
```

Then run the setup script again to update the task.

---

## Monitoring & Logs

### Check if Task Ran

```powershell
Get-ScheduledTaskInfo -TaskName "WebScrapers-NightlyRun"
```

Look at:
- **LastRunTime**: When it last ran
- **LastTaskResult**: 0 = success, other = error
- **NextRunTime**: When it will run next

### View Scraper Logs

Logs are saved in the project folder:

```powershell
# View today's logs
Get-Content logs\meinhausshop.log -Tail 50

# View all recent errors
Select-String -Path logs\*.log -Pattern "ERROR" | Select-Object -Last 20
```

### View Task Scheduler Logs

In Event Viewer:
- Press `Win + R`
- Type `eventvwr.msc`
- Navigate to: Applications and Services Logs → Microsoft → Windows → TaskScheduler → Operational
- Filter by Task Name: `WebScrapers-NightlyRun`

---

## Troubleshooting

### Task Not Running

**Check task status:**
```powershell
Get-ScheduledTask -TaskName "WebScrapers-NightlyRun" | Select-Object State
```

If disabled, enable it:
```powershell
Enable-ScheduledTask -TaskName "WebScrapers-NightlyRun"
```

**Check last run result:**
```powershell
Get-ScheduledTaskInfo -TaskName "WebScrapers-NightlyRun" | Select-Object LastTaskResult
```

- `0` = Success
- `1` = Incorrect function
- `2147942667` = Directory not found
- `2147942402` = File not found

### Python Not Found

If task fails with "Python not found":

1. Find Python path:
   ```powershell
   (Get-Command python).Source
   ```

2. Edit the task in Task Scheduler
3. Change Program/script to full Python path:
   ```
   C:\Users\ahmed\AppData\Local\Programs\Python\Python312\python.exe
   ```

### Permission Errors

Run Task Scheduler as Administrator:
- Press `Win + R`
- Type `taskschd.msc`
- Right-click → Run as administrator

### Task Runs But Scrapers Fail

Test manually first:
```powershell
cd C:\Users\ahmed\Desktop\scrapers
python run_all_scrapers_parallel.py
```

Check for:
- Missing dependencies
- Google Sheets credentials
- Network connectivity

### Computer Sleeping

To prevent computer from sleeping:

**Option 1: Wake computer for task**
- Open Task Scheduler
- Edit task properties
- Conditions tab
- ✓ Wake the computer to run this task

**Option 2: Disable sleep**
- Settings → System → Power & sleep
- Set "When plugged in, PC goes to sleep after" to "Never"

---

## Comparison: Windows vs Linux

| Feature | Windows (Task Scheduler) | Linux (Cron) |
|---------|-------------------------|--------------|
| Setup | GUI or PowerShell | Shell script |
| Scheduling | Flexible, GUI-based | Cron syntax |
| Logging | Event Viewer + file logs | Syslog + file logs |
| Management | Task Scheduler GUI | `crontab` commands |
| Reliability | Excellent | Excellent |
| Wake from sleep | Yes (configurable) | Depends on system |

Both are equally reliable for automated scraping!

---

## Best Practices

### 1. Test Before Scheduling

Always test manually first:
```powershell
python run_all_scrapers_parallel.py
```

### 2. Monitor First Few Runs

Check logs after the first few automated runs:
```powershell
Get-Content logs\*.log -Tail 100
```

### 3. Set Execution Time Limit

In task properties, set a reasonable time limit (6 hours recommended) to prevent hung tasks.

### 4. Enable Email Notifications (Optional)

In Task Scheduler:
- Task properties → Actions tab
- Add action: "Send an e-mail"
- Configure SMTP settings

### 5. Keep Computer On

For reliable execution:
- Keep computer plugged in
- Disable sleep mode, or
- Enable "Wake computer to run this task"

---

## Uninstall

To completely remove the scheduled task:

```powershell
Unregister-ScheduledTask -TaskName "WebScrapers-NightlyRun" -Confirm:$false
```

Or in Task Scheduler:
- Right-click task
- Delete

---

## Summary

✓ **Easy setup** with PowerShell script
✓ **Runs at midnight** every night automatically
✓ **No manual intervention** required
✓ **Reliable** Windows Task Scheduler
✓ **Easy to manage** via GUI or PowerShell
✓ **Logs everything** for monitoring

Your scraping system will now run automatically every night on Windows, just like cron on Linux!
