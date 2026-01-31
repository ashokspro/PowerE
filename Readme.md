# ⚡ Power E - Smart Shutdown Scheduler

**Version 2.0** - A simple, reliable, and professional automatic shutdown scheduler for Windows.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-brightgreen)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📋 Overview

Power E is a lightweight shutdown scheduler that uses Windows Task Scheduler to automatically shut down your computer at a specified time daily. No background processes, no autostart - just clean, simple automation.

### Key Features

✅ **Daily Automatic Shutdowns** - Set once, works every day  
✅ **Customizable Warning** - 30-300 seconds countdown before shutdown  
✅ **Cancellable** - Easy cancel option when warning appears  
✅ **No Background Processes** - Uses Windows Task Scheduler  
✅ **Smart Logging** - Automatic log rotation (max 1MB per file)  
✅ **XML-Based Scheduling** - Works reliably on both laptops and desktops  
✅ **Professional UI** - Clean, modern interface

---

## 📸 Screenshots

### Main Interface
```
┌─────────────────────────────────────────────────┐
│ Tools    Help                          [_][□][X]│
├─────────────────────────────────────────────────┤
│              ⚡ Power E                         │
│        Smart Shutdown Scheduler                 │
├─────────────────────────────────────────────────┤
│  ┌─ Shutdown Time ───────────────────────┐     │
│  │  Hour: [06] Minute: [00] ⚪AM ⚫PM    │     │
│  └───────────────────────────────────────┘     │
│  ┌─ Settings ────────────────────────────┐     │
│  │  Warning time: [60] seconds           │     │
│  └───────────────────────────────────────┘     │
│  ┌──────────────┐  ┌──────────────┐           │
│  │ 🚀 Create    │  │ 🗑️ Delete    │           │
│  │   Schedule   │  │   Schedule   │           │
│  └──────────────┘  └──────────────┘           │
│  ┌─ Status ──────────────────────────────┐     │
│  │ ✅ SCHEDULE ACTIVE                    │     │
│  │ Shutdown Time: 06:00 PM Daily         │     │
│  │ Warning Duration: 60 seconds          │     │
│  └───────────────────────────────────────┘     │
├─────────────────────────────────────────────────┤
│  System: Windows | Python: 3.13                │
└─────────────────────────────────────────────────┘
```

### Warning Popup
```
┌─────────────────────────────────────────────────┐
│        ⚠️ SHUTDOWN WARNING                     │
├─────────────────────────────────────────────────┤
│                                                 │
│      Your computer will shut down soon!         │
│      Please save your work immediately.         │
│                                                 │
│        Shutting down in 60 seconds             │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │ ❌ Cancel    │  │ ⚡ Shutdown  │           │
│  │   Shutdown   │  │     Now      │           │
│  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────┘
```

---

## 💾 Installation

### Requirements
- **Operating System**: Windows 10 or Windows 11
- **Python**: 3.7 or higher
- **Permissions**: Administrator (only when creating/deleting schedules)

### Step-by-Step Installation

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Download Power E**
   - Download `PowerE.py` to a folder (e.g., `C:\PowerE\`)
   - Download `PowerE.bat` to the same folder

3. **Verify Installation**
   ```bash
   python --version
   ```
   Should show Python 3.7 or higher.

**That's it!** No additional dependencies required. Power E uses only Python's standard library.

---

## 🚀 Quick Start Guide

### Creating Your First Schedule

1. **Launch Power E**
   - Double-click `PowerE.bat`
   - Click "Yes" when prompted for administrator privileges
   - ⚠️ Admin is only needed when creating/deleting schedules

2. **Set Shutdown Time**
   - **Hour**: Choose 1-12
   - **Minute**: Choose 00-59
   - **AM/PM**: Select the period
   - Example: `06:00 PM` for 6 PM shutdown

3. **Configure Warning Duration**
   - Choose 30-300 seconds (default: 60 seconds)
   - This is how much warning you'll get before shutdown

4. **Create the Schedule**
   - Click **"🚀 Create Schedule"**
   - Review the settings in the confirmation dialog
   - Click **"Yes"** to confirm

5. **Done!**
   - Status will show **"✅ SCHEDULE ACTIVE"**
   - You can now close Power E
   - Your computer will automatically show a warning at the scheduled time daily

---

## 📖 User Guide

### Understanding the Interface

#### Menu Bar
**Tools Menu:**
- **Open Log Folder** - Opens `%APPDATA%\PowerE` in File Explorer
- **View Activity Log** - Shows user actions (schedules created/deleted, shutdowns)
- **View Debug Log** - Shows technical information for troubleshooting

**Help Menu:**
- **About PowerE** - Version info and features list

#### Main Controls
- **Shutdown Time Section**
  - Set when you want your computer to shut down daily
  - Uses 12-hour format (AM/PM)
  
- **Settings Section**
  - Warning time: How many seconds before shutdown to show the warning
  
- **Buttons**
  - **Create Schedule**: Sets up the daily shutdown (becomes "Update Schedule" when active)
  - **Delete Schedule**: Removes the automatic shutdown

- **Status Display**
  - Shows current schedule status
  - Displays configured time and settings when active

### Daily Operation

When your scheduled time arrives:

1. **Warning Popup Appears**
   - Shows countdown timer
   - Displays warning message
   - Always appears on top of other windows

2. **You Have Two Options:**
   - **❌ Cancel Shutdown**: Closes popup, no shutdown occurs
   - **⚡ Shutdown Now**: Immediately begins shutdown (skips countdown)

3. **If No Action Taken:**
   - Computer shuts down when countdown reaches zero
   - Windows shutdown command executes
   - 5-second grace period for cleanup

4. **Schedule Continues:**
   - Whether cancelled or executed, schedule runs again tomorrow
   - Same time, every day, until you delete the schedule

---

## 🔧 How It Works

### Architecture

```
Power E GUI
    ↓
Windows Task Scheduler
    ↓
PowerE_Warning.bat (runs at scheduled time)
    ↓
PowerE.py --warn (shows warning popup)
    ↓
User Decision
    ↓
[Cancel] or [Shutdown]
```

### Technical Details

1. **No Background Processes**
   - Power E doesn't run in the background
   - Uses Windows Task Scheduler (native Windows service)
   - Zero CPU/RAM usage when not actively running

2. **XML-Based Task Creation**
   - Creates tasks using XML configuration
   - Optimized settings for reliability:
     - `DisallowStartIfOnBatteries: false` (works on battery)
     - `StopIfGoingOnBatteries: false` (won't stop if unplugged)
     - `StartWhenAvailable: true` (retries if PC was busy)

3. **Batch File Approach**
   - `PowerE_Warning.bat` is auto-generated
   - Ensures proper Python execution
   - Tries `pythonw.exe` first (no console), falls back to `python.exe`

4. **Smart Logging**
   - Activity log: User actions and events
   - Debug log: Technical information
   - Auto-rotation: Max 1MB per file
   - Keeps last 50% when rotating

---

## 📂 File Structure

### Application Files
```
PowerE/
├── PowerE.py              # Main Python script
├── PowerE.bat             # Launcher (run this)
└── PowerE_Warning.bat     # Auto-generated by PowerE.py
```

### Data Files
Location: `%APPDATA%\PowerE\`
```
PowerE/
├── config.json       # Your settings
├── activity.log      # User actions log
└── debug.log         # Technical debug log
```

### Accessing Data Folder
1. Press `Win + R`
2. Type: `%APPDATA%\PowerE`
3. Press Enter

---

## 📊 Log Files

### Activity Log (`activity.log`)

**Format:**
```
[2026-01-31 14:00:00] Program Started - Mode: gui (User: ashok)
[2026-01-31 14:00:15] Schedule Created - 02:00 PM (User: ashok)
[2026-01-31 14:00:00] Warning Shown - Countdown: 60s (User: ashok)
[2026-01-31 14:00:30] Shutdown Cancelled - User intervention (User: ashok)
```

**Logged Events:**
- Program Started
- Schedule Created
- Schedule Deleted
- Warning Shown
- Shutdown Cancelled
- Shutdown Executed
- Immediate Shutdown

### Debug Log (`debug.log`)

**Format:**
```
[2026-01-31 14:00:15] Creating task for time: 14:00
[2026-01-31 14:00:15] Task created successfully for 14:00
```

**Logged Information:**
- Task creation details
- Configuration errors
- System exceptions
- Task deletion status

### Log Rotation

- **Trigger**: When file exceeds 1MB
- **Action**: Keeps last 50% of entries
- **Result**: Logs never grow too large
- **Automatic**: No manual cleanup needed

---

## ⚙️ Configuration

### Configuration File
Location: `%APPDATA%\PowerE\config.json`

```json
{
  "hour": "06",
  "minute": "00",
  "ampm": "PM",
  "warning_seconds": 60,
  "enabled": true
}
```

### Manual Editing
While you can edit `config.json` directly, it's recommended to use the GUI. If you do edit manually:
1. Close Power E
2. Edit the file
3. Reopen Power E
4. Delete and recreate the schedule for changes to take effect

---

## ❓ FAQ

### General Questions

**Q: Do I need to keep Power E running?**  
A: No! Once you create the schedule, close Power E. Windows Task Scheduler handles everything.

**Q: Will this work if I'm not logged in?**  
A: The task runs under your user account. You must be logged in for the warning popup to appear.

**Q: What if I'm away when the shutdown time comes?**  
A: The computer will shutdown after the countdown. Make sure to save important work or cancel the schedule if you'll be away.

**Q: Does this work on laptops?**  
A: Yes! Power E uses XML-based scheduling that works on battery power.

**Q: Can I schedule multiple times per day?**  
A: Currently, Power E supports one daily time. For multiple times, you'd need to manually create additional tasks in Task Scheduler.

### Technical Questions

**Q: Why does it need administrator privileges?**  
A: Admin rights are only needed when creating or deleting scheduled tasks in Windows Task Scheduler. The daily shutdown runs without admin.

**Q: Where is the scheduled task stored?**  
A: Task Scheduler Library → `PowerE_AutoShutdown`

**Q: What happens if my PC is asleep at the scheduled time?**  
A: The task won't run if the PC is asleep. Either keep the PC awake or enable "Wake the computer to run this task" in Task Scheduler.

**Q: How do I backup my settings?**  
A: Copy the `%APPDATA%\PowerE` folder to backup all settings and logs.

**Q: Does this consume system resources?**  
A: No! Power E uses zero resources when not running. Task Scheduler is a Windows service always running anyway.

---

## 🐛 Troubleshooting

### Issue: "Access Denied" Error

**Cause**: Running without administrator privileges  
**Solution:**
- Make sure you're running `PowerE.bat` (not PowerE.py directly)
- Click "Yes" when UAC prompts for admin
- If still fails, right-click `PowerE.bat` → "Run as administrator"

### Issue: Warning Popup Doesn't Appear

**Checks:**
1. **Verify task exists**
   - Open Task Scheduler
   - Look for `PowerE_AutoShutdown`

2. **Test manually**
   - In Task Scheduler, right-click the task
   - Click "Run"
   - Popup should appear immediately

3. **Check logs**
   - Tools → View Debug Log
   - Look for error messages

4. **Verify batch file**
   - Check if `PowerE_Warning.bat` exists in PowerE folder
   - If missing, recreate the schedule

### Issue: Computer is Asleep

**Cause**: PC in sleep/hibernate mode at scheduled time  
**Solution:**
- Keep PC awake at scheduled time, OR
- Open Task Scheduler → Task properties → Conditions
- Check "Wake the computer to run this task"

### Issue: Popup Shows But Shutdown Fails

**Cause**: Insufficient shutdown privileges  
**Solution:**
- Check debug log for details
- Ensure shutdown command has proper permissions
- May need to run the task with higher privileges

---

## 🔍 Viewing Logs

### Quick Access
1. Open Power E
2. Go to **Tools** menu
3. Select:
   - **View Activity Log** - User actions
   - **View Debug Log** - Technical info
   - **Open Log Folder** - Browse all files

### Log Locations
- **Windows**: `C:\Users\[YourName]\AppData\Roaming\PowerE\`
- **Quick Access**: Press `Win+R`, type `%APPDATA%\PowerE`

---

## 🗑️ Uninstalling

### Complete Removal

1. **Delete the Schedule**
   ```
   - Open Power E
   - Click "🗑️ Delete Schedule"
   - Confirm deletion
   ```

2. **Delete Application Files**
   ```
   - Delete the PowerE folder (where PowerE.py is located)
   ```

3. **Delete Data Files (Optional)**
   ```
   - Press Win + R
   - Type: %APPDATA%\PowerE
   - Delete the folder
   ```

4. **Verify in Task Scheduler**
   ```
   - Open Task Scheduler
   - Confirm "PowerE_AutoShutdown" is gone
   ```

Power E is now completely removed from your system.

---

## 🤝 Advanced Usage

### Customizing Warning Message

Edit the `ShutdownWarning` class in `PowerE.py`:
```python
# Around line 760
tk.Label(
    content,
    text="Your computer will shut down soon!",  # Change this
    ...
```

### Changing Shutdown Command

Edit the `execute_shutdown` method:
```python
# Around line 860
# For Windows:
subprocess.run(['shutdown', '/s', '/t', '5'], check=True)

# Options:
# /s - Shutdown
# /r - Restart
# /h - Hibernate
# /t X - Wait X seconds
```

### Multiple Schedules

Create additional tasks manually in Task Scheduler:
1. Open Task Scheduler
2. Action → Create Task
3. Name: `PowerE_Evening` (or any name)
4. Triggers → Daily at your time
5. Actions → Start program: `PowerE_Warning.bat`
6. Settings → Uncheck battery restrictions

---

## 📝 Version History

### Version 2.0 (Current)
- ✅ XML-based task scheduling (laptop/battery compatible)
- ✅ Improved log system with auto-rotation
- ✅ Separate activity and debug logs
- ✅ Professional menu bar
- ✅ Cleaner UI (removed test button)
- ✅ Better error handling and logging
- ✅ Optimized for reliability

### Version 1.0
- Basic scheduling functionality
- CSV-based logging
- Simple task creation
- GUI interface

---

## 🎯 Best Practices

### For Daily Use

1. **Set realistic times**
   - Choose a time when you're usually done working
   - Leave buffer for occasional late sessions

2. **Use adequate warning**
   - Minimum 60 seconds recommended
   - Gives time to save work and cancel if needed

3. **Check logs occasionally**
   - Helps identify any issues early
   - Tools → View Activity Log

4. **Keep Power E folder intact**
   - Don't move files after creating schedule
   - If you must move, delete and recreate schedule

### For Laptop Users

- ✅ Works perfectly on battery power
- ✅ No special configuration needed
- ✅ XML scheduling handles battery scenarios automatically

### For Power Users

- Back up `%APPDATA%\PowerE` folder regularly
- Review debug logs for optimization opportunities
- Customize shutdown command for restart/hibernate options
- Create multiple schedules via Task Scheduler

---

## 🔒 Privacy & Security

### What Power E Does
- ✅ Creates scheduled tasks in Windows Task Scheduler
- ✅ Writes logs to `%APPDATA%\PowerE`
- ✅ Reads/writes configuration in user's AppData

### What Power E Doesn't Do
- ❌ No internet connection
- ❌ No data collection
- ❌ No background processes
- ❌ No access to personal files
- ❌ No system modifications beyond Task Scheduler

### Data Storage
All data stays on your computer:
- Configuration: Local JSON file
- Logs: Local text files
- Task: Windows Task Scheduler (standard Windows feature)

---

## 📄 License

MIT License

Copyright (c) 2026 Power E

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🌟 Features Summary

| Feature | Description |
|---------|-------------|
| **Daily Scheduling** | Set once, runs every day |
| **Customizable Warning** | 30-300 seconds countdown |
| **Cancel Anytime** | Easy cancel in warning popup |
| **No Background Process** | Zero CPU/RAM when idle |
| **Smart Logging** | Auto-rotation at 1MB |
| **Battery Compatible** | Works on laptops unplugged |
| **Professional UI** | Clean, modern interface |
| **Easy Access Logs** | Menu-based log viewing |
| **Reliable** | Uses native Windows scheduler |
| **Lightweight** | No dependencies |

---

## 💡 Tips & Tricks

### Tip 1: Quick Schedule Changes
To change only the time without opening the full UI, update the time and click "Update Schedule" directly.

### Tip 2: Temporary Disable
Instead of deleting, temporarily disable in Task Scheduler:
- Open Task Scheduler
- Find `PowerE_AutoShutdown`
- Right-click → Disable

### Tip 3: Emergency Cancel
If you forgot about the schedule and see the warning:
- Just click "Cancel Shutdown"
- The schedule continues for tomorrow

### Tip 4: View Task Details
To see full task configuration:
- Open Task Scheduler
- Find `PowerE_AutoShutdown`
- Double-click to view all settings

---

## 🎓 Understanding Task Scheduler

Power E leverages Windows Task Scheduler, a robust built-in feature:

- **Reliable**: Used by Windows for system tasks
- **Efficient**: No additional overhead
- **Standard**: Industry-standard scheduling
- **Flexible**: Can be modified manually if needed

To learn more:
1. Open Task Scheduler (search in Start menu)
2. Navigate to Task Scheduler Library
3. Find `PowerE_AutoShutdown`
4. Explore the settings

---

## 📞 Support

### Getting Help

1. **Check this README** - Most questions answered here
2. **View Debug Log** - Tools → View Debug Log  
3. **Check Activity Log** - Tools → View Activity Log
4. **Review FAQ** - See FAQ section above

### Reporting Issues

When reporting issues, include:
- Windows version
- Python version (`python --version`)
- Debug log contents
- Steps to reproduce
- Expected vs actual behavior

---

## 🎉 Thank You!

Thank you for using Power E! We hope it helps you maintain a healthy shutdown schedule for your computer.

**⚡ Power E - Simple. Reliable. Professional.**

---

*Version 2.0 | Last updated: January 31, 2026*
*Made with ❤️ for everyone who needs automatic shutdowns*