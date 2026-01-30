#!/usr/bin/env python3
"""
Power E - Smart Shutdown Scheduler
Version 2.0 - Task Scheduler Fix

Two modes only:
1. GUI mode (default): Configure and manage scheduled shutdowns
2. --warn mode: Show warning popup at scheduled time

No background processes. No autostart. Clean and simple.
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import subprocess
import json
import os
import sys
import platform
from pathlib import Path
import argparse
import csv
import traceback


class PowerEConfig:
    """Configuration management"""
    
    def __init__(self):
        # Use AppData on Windows, home directory on others
        if platform.system() == "Windows":
            base = Path(os.getenv("APPDATA", Path.home()))
        else:
            base = Path.home()
        
        self.app_dir = base / "PowerE"
        self.app_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.app_dir / "config.json"
        self.log_file = self.app_dir / "shutdown_log.csv"
        self.error_log = self.app_dir / "error_log.txt"  # NEW: Error logging
    
    def log_error(self, error_msg):
        """Log errors to file for debugging"""
        try:
            with open(self.error_log, 'a') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Error: {error_msg}\n")
                f.write(f"{'='*60}\n")
        except:
            pass
    
    def load(self):
        """Load configuration"""
        defaults = {
            'hour': '06',
            'minute': '00',
            'ampm': 'PM',
            'warning_seconds': 60,
            'enabled': False
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    return {**defaults, **config}
        except Exception as e:
            self.log_error(f"Config load error: {e}")
        
        return defaults
    
    def save(self, config):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            self.log_error(f"Config save error: {e}")
            return False
    
    def log_action(self, action, details=""):
        """Log action to CSV"""
        try:
            file_exists = self.log_file.exists()
            
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                
                if not file_exists:
                    writer.writerow(['Timestamp', 'Action', 'Details', 'User'])
                
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    action,
                    details,
                    os.getlogin()
                ])
        except Exception as e:
            self.log_error(f"Action log error: {e}")


class TaskSchedulerManager:
    """Manages Windows Task Scheduler operations"""
    
    TASK_NAME = "PowerE_AutoShutdown"
    
    def __init__(self):
        self.script_path = Path(__file__).resolve()
        self.script_dir = self.script_path.parent
        self.python_exe = sys.executable
        self.config_mgr = PowerEConfig()
        
        # Create the warning batch file if it doesn't exist
        self.warning_bat = self.script_dir / "PowerE_Warning.bat"
        self._create_warning_bat()
    
    def _create_warning_bat(self):
        """Create the PowerE_Warning.bat file"""
        bat_content = '''@echo off
REM PowerE Warning Launcher
REM This is called by Task Scheduler to show the shutdown warning

REM Change to script directory
cd /d "%~dp0"

REM Try pythonw.exe first (no console)
pythonw.exe PowerE.py --warn
set EXITCODE=%errorLevel%

REM If pythonw.exe failed, try python.exe
if %EXITCODE% neq 0 (
    python.exe PowerE.py --warn
    set EXITCODE=%errorLevel%
)

REM Log to file if error
if %EXITCODE% neq 0 (
    echo Error: Exit code %EXITCODE% at %date% %time% >> PowerE_bat_errors.log
)

exit /b %EXITCODE%
'''
        try:
            with open(self.warning_bat, 'w') as f:
                f.write(bat_content)
        except Exception as e:
            self.config_mgr.log_error(f"Failed to create warning bat: {e}")
    
    def create_task(self, hour, minute, ampm):
        """Create scheduled task to run PowerE with --warn flag"""
        
        # Convert to 24-hour format
        hour_24 = int(hour)
        if ampm == 'PM' and hour_24 != 12:
            hour_24 += 12
        elif ampm == 'AM' and hour_24 == 12:
            hour_24 = 0
        
        # Format time as HH:MM
        time_str = f"{hour_24:02d}:{minute}"
        
        # Delete existing task if any
        self.delete_task()
        
        # Use the batch file instead of calling Python directly
        # This avoids the need for /RL HIGHEST and admin privileges
        cmd = [
            'schtasks',
            '/Create',
            '/TN', self.TASK_NAME,
            '/TR', f'"{self.warning_bat}"',
            '/SC', 'DAILY',
            '/ST', time_str,
            '/F'  # Force create (overwrites if exists)
            # No /RL HIGHEST - runs with normal user privileges
        ]
        
        try:
            self.config_mgr.log_error(f"Creating task with command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.config_mgr.log_error(f"Task created successfully")
                return True, "Schedule created successfully"
            else:
                error_msg = f"Failed to create schedule: {result.stderr}"
                self.config_mgr.log_error(error_msg)
                return False, error_msg
        
        except subprocess.TimeoutExpired:
            error_msg = "Task scheduler command timed out"
            self.config_mgr.log_error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error creating schedule: {str(e)}\n{traceback.format_exc()}"
            self.config_mgr.log_error(error_msg)
            return False, f"Error creating schedule: {str(e)}"
    
    def delete_task(self):
        """Delete scheduled task"""
        cmd = [
            'schtasks',
            '/Delete',
            '/TN', self.TASK_NAME,
            '/F'  # Force delete without confirmation
        ]
        
        try:
            subprocess.run(
                cmd,
                capture_output=True,
                timeout=5
            )
            return True
        except Exception as e:
            self.config_mgr.log_error(f"Delete task error: {e}")
            return False
    
    def task_exists(self):
        """Check if task exists"""
        cmd = [
            'schtasks',
            '/Query',
            '/TN', self.TASK_NAME
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_task_info(self):
        """Get task information"""
        if not self.task_exists():
            return None
        
        cmd = [
            'schtasks',
            '/Query',
            '/TN', self.TASK_NAME,
            '/FO', 'LIST',
            '/V'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout
            
        except:
            pass
        
        return None


class PowerEGUI:
    """Main GUI application"""
    
    def __init__(self, root):
        self.root = root
        self.config_mgr = PowerEConfig()
        self.scheduler = TaskSchedulerManager()
        self.config = self.config_mgr.load()
        
        self.setup_window()
        self.create_widgets()
        self.update_status()
    
    def setup_window(self):
        """Setup main window"""
        self.root.title("Power E - Shutdown Scheduler v2.0")
        self.root.geometry("600x520")
        self.root.resizable(False, False)
        
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Open Log Folder", command=self.open_log_folder)
        tools_menu.add_command(label="View Error Log", command=self.view_error_log)
        tools_menu.add_command(label="View Activity Log", command=self.view_activity_log)
        tools_menu.add_separator()
        tools_menu.add_command(label="Test Warning Popup", command=self.test_warning)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About PowerE", command=self.show_about)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (520 // 2)
        self.root.geometry(f"600x520+{x}+{y}")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#2C3E50', height=90)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="⚡ Power E",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#2C3E50'
        ).pack(pady=10)
        
        tk.Label(
            title_frame,
            text="Smart Shutdown Scheduler",
            font=('Arial', 10),
            fg='#BDC3C7',
            bg='#2C3E50'
        ).pack()
        
        # Main content
        content = tk.Frame(self.root, padx=30, pady=15)
        content.pack(fill='both', expand=True)
        
        # Time selection
        time_frame = tk.LabelFrame(
            content,
            text="Shutdown Time",
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=12
        )
        time_frame.pack(fill='x', pady=(0, 15))
        
        time_inputs = tk.Frame(time_frame)
        time_inputs.pack()
        
        # Hour
        tk.Label(time_inputs, text="Hour:", font=('Arial', 10)).grid(row=0, column=0, padx=5)
        self.hour_var = tk.StringVar(value=self.config['hour'])
        hour_spin = tk.Spinbox(
            time_inputs,
            from_=1,
            to=12,
            textvariable=self.hour_var,
            width=5,
            font=('Arial', 12, 'bold'),
            justify='center'
        )
        hour_spin.grid(row=0, column=1, padx=5)
        
        # Minute
        tk.Label(time_inputs, text="Minute:", font=('Arial', 10)).grid(row=0, column=2, padx=5)
        self.minute_var = tk.StringVar(value=self.config['minute'])
        minute_spin = tk.Spinbox(
            time_inputs,
            from_=0,
            to=59,
            textvariable=self.minute_var,
            width=5,
            font=('Arial', 12, 'bold'),
            justify='center',
            format='%02.0f'
        )
        minute_spin.grid(row=0, column=3, padx=5)
        
        # AM/PM
        self.ampm_var = tk.StringVar(value=self.config['ampm'])
        am_rb = tk.Radiobutton(
            time_inputs,
            text="AM",
            variable=self.ampm_var,
            value="AM",
            font=('Arial', 10)
        )
        am_rb.grid(row=0, column=4, padx=5)
        
        pm_rb = tk.Radiobutton(
            time_inputs,
            text="PM",
            variable=self.ampm_var,
            value="PM",
            font=('Arial', 10)
        )
        pm_rb.grid(row=0, column=5, padx=5)
        
        # Settings
        settings_frame = tk.LabelFrame(
            content,
            text="Settings",
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=12
        )
        settings_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            settings_frame,
            text="Warning time before shutdown:",
            font=('Arial', 10)
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        self.warning_var = tk.StringVar(value=str(self.config['warning_seconds']))
        warning_spin = tk.Spinbox(
            settings_frame,
            from_=30,
            to=300,
            increment=30,
            textvariable=self.warning_var,
            width=8,
            font=('Arial', 10)
        )
        warning_spin.grid(row=0, column=1, padx=10)
        
        tk.Label(settings_frame, text="seconds", font=('Arial', 10)).grid(row=0, column=2)
        
        # Control buttons
        button_frame = tk.Frame(content)
        button_frame.pack(fill='x', pady=(0, 15))
        
        self.create_btn = tk.Button(
            button_frame,
            text="🚀 Create Schedule",
            command=self.create_schedule,
            font=('Arial', 12, 'bold'),
            bg='#27AE60',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            relief='raised',
            bd=3
        )
        self.create_btn.pack(side='left', padx=5, expand=True, fill='x')
        
        self.delete_btn = tk.Button(
            button_frame,
            text="🗑️ Delete Schedule",
            command=self.delete_schedule,
            font=('Arial', 12, 'bold'),
            bg='#E74C3C',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            relief='raised',
            bd=3,
            state='disabled'
        )
        self.delete_btn.pack(side='left', padx=5, expand=True, fill='x')
        
        # Status display
        status_frame = tk.LabelFrame(
            content,
            text="Status",
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=10
        )
        status_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.status_text = tk.Text(
            status_frame,
            height=6,
            font=('Courier', 9),
            bg='#F8F9FA',
            relief='flat',
            wrap='word'
        )
        self.status_text.pack(fill='both', expand=True)
        self.status_text.config(state='disabled')
        
        # Footer
        footer = tk.Frame(self.root, bg='#ECF0F1', height=40)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
        
        tk.Label(
            footer,
            text=f"System: {platform.system()} | Python: {sys.version.split()[0]}",
            font=('Arial', 8),
            bg='#ECF0F1',
            fg='#7F8C8D'
        ).pack(pady=10)
    
    def update_status_text(self, message):
        """Update status text widget"""
        self.status_text.config(state='normal')
        self.status_text.delete('1.0', 'end')
        self.status_text.insert('1.0', message)
        self.status_text.config(state='disabled')
    
    def open_log_folder(self):
        """Open the log folder in file explorer"""
        try:
            if platform.system() == "Windows":
                os.startfile(self.config_mgr.app_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', self.config_mgr.app_dir])
            else:  # Linux
                subprocess.run(['xdg-open', self.config_mgr.app_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open log folder:\n{e}")
    
    def view_error_log(self):
        """View error log"""
        try:
            if self.config_mgr.error_log.exists():
                if platform.system() == "Windows":
                    os.startfile(self.config_mgr.error_log)
                else:
                    subprocess.run(['open', self.config_mgr.error_log])
            else:
                messagebox.showinfo("No Errors", "No error log found. Everything is working fine!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open error log:\n{e}")
    
    def view_activity_log(self):
        """View activity log"""
        try:
            if self.config_mgr.log_file.exists():
                if platform.system() == "Windows":
                    os.startfile(self.config_mgr.log_file)
                else:
                    subprocess.run(['open', self.config_mgr.log_file])
            else:
                messagebox.showinfo("No Activity", "No activity log found yet.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open activity log:\n{e}")
    
    def test_warning(self):
        """Test the warning popup"""
        if messagebox.askyesno(
            "Test Warning",
            "This will show the shutdown warning popup.\n\n"
            "You can test the countdown and cancel functionality.\n"
            "No actual shutdown will occur.\n\n"
            "Continue?"
        ):
            # Run the warning in test mode
            warning = ShutdownWarning(test_mode=True)
            warning.run()
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""Power E - Shutdown Scheduler
Version 2.0

A simple and reliable tool for scheduling automatic shutdowns.

Features:
• Daily scheduled shutdowns
• Customizable warning time
• Easy to use interface
• Detailed logging

Log Location:
{self.config_mgr.app_dir}

© 2026 Power E
"""
        messagebox.showinfo("About Power E", about_text)
    
    def update_status(self):
        """Update status display"""
        if self.scheduler.task_exists():
            hour = self.config['hour']
            minute = self.config['minute']
            ampm = self.config['ampm']
            
            status = f"""✅ SCHEDULE ACTIVE

Shutdown Time: {hour}:{minute} {ampm} Daily
Warning Duration: {self.config['warning_seconds']} seconds

The computer will show a warning at the scheduled time.
You can cancel the shutdown when the popup appears.

Task: PowerE_AutoShutdown"""
            
            self.create_btn.config(text="🔄 Update Schedule")
            self.delete_btn.config(state='normal')
        else:
            status = """⏸️ NO ACTIVE SCHEDULE

Click "Create Schedule" to set up automatic daily
shutdown at your preferred time.

Configure the time and warning duration above,
then click the button to activate."""
            
            self.create_btn.config(text="🚀 Create Schedule")
            self.delete_btn.config(state='disabled')
        
        self.update_status_text(status)
    
    def validate_time(self):
        """Validate time inputs"""
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            
            if not (1 <= hour <= 12):
                return False, "Hour must be between 1 and 12"
            
            if not (0 <= minute <= 59):
                return False, "Minute must be between 0 and 59"
            
            return True, ""
        
        except ValueError:
            return False, "Invalid time format"
    
    def create_schedule(self):
        """Create or update scheduled shutdown"""
        
        # Validate input
        valid, error = self.validate_time()
        if not valid:
            messagebox.showerror("Invalid Input", error)
            return
        
        hour = self.hour_var.get().zfill(2)
        minute = self.minute_var.get().zfill(2)
        ampm = self.ampm_var.get()
        warning = self.warning_var.get()
        
        # Confirm
        action = "update" if self.scheduler.task_exists() else "create"
        
        if not messagebox.askyesno(
            "Confirm",
            f"Do you want to {action} the shutdown schedule?\n\n"
            f"Time: {hour}:{minute} {ampm}\n"
            f"Warning: {warning} seconds\n"
            f"Frequency: Daily",
            icon='question'
        ):
            return
        
        # Create task
        success, message = self.scheduler.create_task(hour, minute, ampm)
        
        if success:
            # Save config
            self.config = {
                'hour': hour,
                'minute': minute,
                'ampm': ampm,
                'warning_seconds': int(warning),
                'enabled': True
            }
            self.config_mgr.save(self.config)
            self.config_mgr.log_action("Schedule Created", f"{hour}:{minute} {ampm}")
            
            messagebox.showinfo(
                "Success",
                f"Shutdown schedule {action}d successfully!\n\n"
                f"Your computer will show a warning at {hour}:{minute} {ampm} daily.\n"
                f"You'll have {warning} seconds to cancel if needed.\n\n"
                f"Tip: Use Tools → Test Warning Popup to verify!"
            )
            
            self.update_status()
        else:
            messagebox.showerror("Error", message)
    
    def delete_schedule(self):
        """Delete scheduled shutdown"""
        
        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete the shutdown schedule?\n\n"
            "Automatic shutdowns will stop.",
            icon='warning'
        ):
            return
        
        if self.scheduler.delete_task():
            self.config['enabled'] = False
            self.config_mgr.save(self.config)
            self.config_mgr.log_action("Schedule Deleted", "")
            
            messagebox.showinfo(
                "Success",
                "Shutdown schedule deleted successfully!\n\n"
                "Automatic shutdowns have been disabled."
            )
            
            self.update_status()
        else:
            messagebox.showerror(
                "Error",
                "Failed to delete schedule.\n"
                "You may need to run as Administrator."
            )


class ShutdownWarning:
    """Warning popup shown at scheduled shutdown time"""
    
    def __init__(self, test_mode=False):
        self.config_mgr = PowerEConfig()
        self.config = self.config_mgr.load()
        self.countdown = self.config.get('warning_seconds', 60)
        self.cancelled = False
        self.test_mode = test_mode
        
        # Log that warning was triggered
        self.config_mgr.log_action("Warning Shown", f"Countdown: {self.countdown}s, Test: {test_mode}")
        
        # Create popup window
        self.root = tk.Tk()
        self.root.title("Shutdown Warning" + (" - TEST MODE" if test_mode else ""))
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Make it topmost
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"600x400+{x}+{y}")
        
        # Override close button
        self.root.protocol("WM_DELETE_WINDOW", self.cancel_shutdown)
        
        self.create_widgets()
        self.start_countdown()
    
    def create_widgets(self):
        """Create warning UI"""
        
        # Warning header
        header_color = '#3498DB' if self.test_mode else '#E74C3C'
        header = tk.Frame(self.root, bg=header_color, height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        header_text = "🧪 TEST MODE - SHUTDOWN WARNING" if self.test_mode else "⚠️ SHUTDOWN WARNING"
        tk.Label(
            header,
            text=header_text,
            font=('Arial', 18 if self.test_mode else 20, 'bold'),
            fg='white',
            bg=header_color
        ).pack(pady=25)
        
        # Content
        content = tk.Frame(self.root, padx=30, pady=20)
        content.pack(fill='both', expand=True)
        
        # Message
        if self.test_mode:
            msg = "Testing shutdown warning popup"
            submsg = "No actual shutdown will occur"
        else:
            msg = "Your computer will shut down soon!"
            submsg = "Please save your work immediately."
        
        tk.Label(
            content,
            text=msg,
            font=('Arial', 14, 'bold'),
            fg='#2C3E50'
        ).pack(pady=(0, 10))
        
        tk.Label(
            content,
            text=submsg,
            font=('Arial', 11),
            fg='#7F8C8D'
        ).pack(pady=(0, 20))
        
        # Countdown
        self.countdown_label = tk.Label(
            content,
            text=f"{'Test countdown' if self.test_mode else 'Shutting down'} in {self.countdown} seconds",
            font=('Arial', 16, 'bold'),
            fg='#3498DB' if self.test_mode else '#E74C3C'
        )
        self.countdown_label.pack(pady=20)
        
        # Buttons
        button_frame = tk.Frame(content)
        button_frame.pack(pady=30, fill='x')
        
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancel" + (" Test" if self.test_mode else " Shutdown"),
            command=self.cancel_shutdown,
            font=('Arial', 12, 'bold'),
            bg='#27AE60',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            relief='raised',
            bd=3
        )
        cancel_btn.pack(side='left', padx=5, expand=True, fill='x')
        
        if not self.test_mode:
            shutdown_btn = tk.Button(
                button_frame,
                text="⚡ Shutdown Now",
                command=self.shutdown_now,
                font=('Arial', 12, 'bold'),
                bg='#E74C3C',
                fg='white',
                padx=20,
                pady=10,
                cursor='hand2',
                relief='raised',
                bd=3
            )
            shutdown_btn.pack(side='left', padx=5, expand=True, fill='x')
    
    def start_countdown(self):
        """Start countdown timer"""
        if self.countdown > 0 and not self.cancelled:
            prefix = "Test countdown" if self.test_mode else "Shutting down"
            self.countdown_label.config(
                text=f"{prefix} in {self.countdown} seconds"
            )
            self.countdown -= 1
            self.root.after(1000, self.start_countdown)
        elif not self.cancelled:
            # Time's up
            if self.test_mode:
                messagebox.showinfo(
                    "Test Complete",
                    "Test countdown completed!\n\n"
                    "In real mode, the computer would shutdown now."
                )
                self.root.destroy()
            else:
                self.execute_shutdown()
    
    def cancel_shutdown(self):
        """Cancel the shutdown"""
        self.cancelled = True
        self.config_mgr.log_action("Shutdown Cancelled", "User intervention")
        
        msg = "The test has been cancelled." if self.test_mode else "The shutdown has been cancelled.\n\nThe schedule is still active and will run again tomorrow."
        
        messagebox.showinfo(
            "Cancelled",
            msg
        )
        
        self.root.destroy()
    
    def shutdown_now(self):
        """Shutdown immediately"""
        self.config_mgr.log_action("Immediate Shutdown", "User initiated")
        self.execute_shutdown()
    
    def execute_shutdown(self):
        """Execute system shutdown"""
        self.config_mgr.log_action("Shutdown Executed", "")
        
        try:
            if platform.system() == "Windows":
                # Shutdown in 5 seconds to give time for cleanup
                subprocess.run(['shutdown', '/s', '/t', '5'], check=True)
            elif platform.system() == "Linux":
                subprocess.run(['shutdown', '-h', '+1'], check=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['sudo', 'shutdown', '-h', '+1'], check=True)
            
            self.root.destroy()
        
        except Exception as e:
            error_msg = f"Failed to execute shutdown:\n{str(e)}\n\n"
            error_msg += "You may need administrator privileges."
            
            self.config_mgr.log_error(f"Shutdown execution failed: {e}\n{traceback.format_exc()}")
            
            messagebox.showerror(
                "Shutdown Failed",
                error_msg
            )
    
    def run(self):
        """Run the warning popup"""
        self.root.mainloop()


def main():
    """Main entry point"""
    
    # Set up logging for any uncaught exceptions
    config_mgr = PowerEConfig()
    
    def exception_handler(exc_type, exc_value, exc_traceback):
        """Log uncaught exceptions"""
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        config_mgr.log_error(f"Uncaught exception:\n{error_msg}")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = exception_handler
    
    try:
        parser = argparse.ArgumentParser(description='Power E - Shutdown Scheduler')
        parser.add_argument(
            '--warn',
            action='store_true',
            help='Show shutdown warning (used by Task Scheduler)'
        )
        
        args = parser.parse_args()
        
        config_mgr.log_action("Program Started", f"Mode: {'warn' if args.warn else 'gui'}")
        
        if args.warn:
            # Warning mode - show countdown and shutdown
            warning = ShutdownWarning(test_mode=False)
            warning.run()
        else:
            # GUI mode - configure schedules
            root = tk.Tk()
            app = PowerEGUI(root)
            root.mainloop()
    
    except Exception as e:
        config_mgr.log_error(f"Main error: {e}\n{traceback.format_exc()}")
        raise


if __name__ == "__main__":
    main()