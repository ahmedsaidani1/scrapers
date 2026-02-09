"""
Simple Python script to set up Shopify automation task.
Run this instead of the PowerShell script.
"""
import os
import sys
import subprocess
from datetime import datetime, timedelta

print("=" * 70)
print("SHOPIFY AUTOMATION SETUP")
print("=" * 70)

# Get credentials
print("\nEnter your Shopify admin credentials:")
email = input("Shopify Admin Email: ").strip()
password = input("Shopify Admin Password: ").strip()
markup = input("Price Markup % (default 20): ").strip() or "20"

if not email or not password:
    print("\n❌ Email and password are required!")
    sys.exit(1)

print(f"\n✓ Credentials received")
print(f"✓ Price markup: {markup}%")

# Get script paths
script_dir = os.path.dirname(os.path.abspath(__file__))
python_script = os.path.join(script_dir, "shopify_sync_from_sheets.py")

if not os.path.exists(python_script):
    print(f"\n❌ Error: {python_script} not found!")
    sys.exit(1)

print(f"✓ Found sync script")

# Ask if user wants to test first
test_first = input("\nRun a test sync first? (y/n): ").strip().lower()

if test_first == 'y':
    print("\n" + "=" * 70)
    print("RUNNING TEST SYNC")
    print("=" * 70)
    print("\nThis will test the sync process...")
    print("(This may take a few minutes)\n")
    
    try:
        result = subprocess.run(
            ["python", python_script, email, password, markup],
            cwd=script_dir,
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✓ Test completed successfully!")
        else:
            print("\n⚠ Test had some issues")
        
        proceed = input("\nProceed with automation setup? (y/n): ").strip().lower()
        if proceed != 'y':
            print("\nSetup cancelled.")
            sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        proceed = input("\nContinue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            sys.exit(1)

# Create scheduled task using PowerShell
print("\n" + "=" * 70)
print("CREATING SCHEDULED TASK")
print("=" * 70)

task_name = "Shopify_Sync_After_Scrapers"

# Build PowerShell command to create task
trigger_time = "04:00"  # 4 AM (2 hours after 2 AM scrapers)

ps_command = f'''
$TaskName = "{task_name}"
$Action = New-ScheduledTaskAction -Execute "python" -Argument '"{python_script}" "{email}" "{password}" {markup}' -WorkingDirectory "{script_dir}"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At {trigger_time}
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {{
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}}

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Sync Google Sheets to Shopify" -User $env:USERNAME -RunLevel Highest
'''

try:
    print("\nCreating Windows scheduled task...")
    result = subprocess.run(
        ["powershell", "-Command", ps_command],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ Task created successfully!")
    else:
        print(f"⚠ Task creation had issues: {result.stderr}")
        print("\nYou can create the task manually using Task Scheduler.")
        
except Exception as e:
    print(f"❌ Error creating task: {e}")
    print("\nYou can create the task manually using Task Scheduler.")

# Summary
print("\n" + "=" * 70)
print("SETUP COMPLETE!")
print("=" * 70)

print(f"\nTask Configuration:")
print(f"  Name: {task_name}")
print(f"  Schedule: Every Sunday at {trigger_time}")
print(f"  Price Markup: {markup}%")
print(f"  Email: {email}")

print(f"\nAutomated Workflow:")
print(f"  1. Scrapers run at 2:00 AM")
print(f"  2. Shopify sync runs at {trigger_time}")
print(f"  3. Products uploaded to Shopify as drafts")

print(f"\nManual Commands:")
print(f"  Test now:")
print(f'    python shopify_sync_from_sheets.py "{email}" "****" {markup}')
print(f"\n  Run task now:")
print(f'    Start-ScheduledTask -TaskName "{task_name}"')
print(f"\n  Check task:")
print(f'    Get-ScheduledTask -TaskName "{task_name}"')

print("\n✓ Automation is ready!")
print("=" * 70)
