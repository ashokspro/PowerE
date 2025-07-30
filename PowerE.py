import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import threading
import time
import os
import platform
import subprocess
import json
import csv
import argparse

class ShutdownScheduler:
    def __init__(self, root=None, headless_mode=False):
        self.headless_mode = headless_mode
        self.root = root

        # Configuration file for persistence
        self.config_file = "scheduler_config.json"

        # Time input parts
        self.hour_var = None
        self.minute_var = None
        self.ampm_var = None
        self.selected_part = 'hour'

        self.shutdown_time = None
        self.timer_thread = None
        self.stop_thread = threading.Event()
        self.is_scheduler_running = False
        self.daily_mode = True

        # Load saved configuration first
        self.load_config()

        if not headless_mode and root:
            # GUI mode - initialize GUI variables
            self.hour_var = tk.StringVar(value=self.saved_hour)
            self.minute_var = tk.StringVar(value=self.saved_minute)
            self.ampm_var = tk.StringVar(value=self.saved_ampm)

            self.root.title("Power E v1.0")
            self.root.geometry("500x500+520+200")
            self.root.resizable(False, False)

            # Style configuration
            self.normal_bg = 'white'
            self.selected_bg = '#4A90E2'
            self.selected_fg = 'white'
            self.normal_fg = 'black'

            self.create_widgets()
            self.update_selection_highlight()
        else:
            # Headless mode
            self.run_headless()

    def load_config(self):
        """Load saved configuration from file"""
        # Default values
        self.saved_hour = '06'
        self.saved_minute = '00'
        self.saved_ampm = 'PM'

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.saved_hour = config.get('hour', '06')
                    self.saved_minute = config.get('minute', '00')
                    self.saved_ampm = config.get('ampm', 'PM')
        except Exception:
            pass  # Use defaults if loading fails

    def save_config(self):
        """Save current configuration to file"""
        try:
            if self.headless_mode:
                # In headless mode, save the loaded values
                config = {
                    'hour': self.saved_hour,
                    'minute': self.saved_minute,
                    'ampm': self.saved_ampm
                }
            else:
                # In GUI mode, save the current GUI values
                config = {
                    'hour': self.hour_var.get(),
                    'minute': self.minute_var.get(),
                    'ampm': self.ampm_var.get()
                }
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception:
            pass  # Ignore save errors

    def run_headless(self):
        """Run in headless mode without GUI"""
        print("Power E running in headless mode...")

        # Check if config exists
        if not os.path.exists(self.config_file):
            print("No configuration found. Please run with GUI first to set up your shutdown time.")
            return

        # Start scheduler automatically
        self.start_headless_scheduler()

        # Keep the program running
        try:
            while not self.stop_thread.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down scheduler...")
            self.stop_thread.set()

    def start_headless_scheduler(self):
        """Start scheduler in headless mode"""
        try:
            self.shutdown_time = self.get_next_shutdown_datetime()
            print(f"Daily shutdown scheduled for {self.shutdown_time.strftime('%I:%M %p')}")

            self.is_scheduler_running = True
            self.stop_thread.clear()

            self.timer_thread = threading.Thread(target=self.headless_countdown_loop, daemon=True)
            self.timer_thread.start()

        except Exception as e:
            print(f"Failed to start headless scheduler: {str(e)}")

    def headless_countdown_loop(self):
        """Countdown loop for headless mode"""
        while not self.stop_thread.is_set():
            now = datetime.now()
            diff = self.shutdown_time - now

            if diff.total_seconds() <= 0:
                print("Executing shutdown...")
                self.perform_shutdown()
                if self.daily_mode and not self.stop_thread.is_set():
                    self.schedule_next_day()
                return
            else:
                hours, remainder = divmod(int(diff.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                # Print status every 10 minutes or in last 5 minutes
                if (minutes % 10 == 0 and seconds == 0) or diff.total_seconds() <= 300:
                    print(f"Next shutdown in: {hours:02d}:{minutes:02d}:{seconds:02d}")

            time.sleep(1)

    def create_widgets(self):
        # Title frame
        title_frame = tk.Frame(self.root, bg='#2C3E50')
        title_frame.pack(fill='x', pady=(0, 20))

        title_label = tk.Label(title_frame, text="Power E ⚡",
                               font=('Arial', 16, 'bold'), fg='white', bg='#2C3E50')
        title_label.pack(pady=15)

        # Main time display frame
        main_time_frame = tk.Frame(self.root)
        main_time_frame.pack(pady=20)

        # Time display with buttons
        time_container = tk.Frame(main_time_frame)
        time_container.pack()

        # Time display frame
        time_frame = tk.Frame(time_container)
        time_frame.pack(side='left', padx=20)

        # Editable hour entry
        self.hour_entry = tk.Entry(time_frame, textvariable=self.hour_var, width=3,
                                   font=('Arial', 24, 'bold'), justify='center', relief='raised', bd=2)
        self.hour_entry.pack(side='left')
        self.hour_entry.bind('<FocusIn>', lambda e: self.select_part('hour'))
        self.hour_entry.bind('<KeyPress>', self.validate_hour_keypress)
        self.hour_entry.bind('<FocusOut>', self.validate_hour_input)

        # Colon separator
        tk.Label(time_frame, text=":", font=('Arial', 24, 'bold')).pack(side='left')

        # Editable minute entry
        self.minute_entry = tk.Entry(time_frame, textvariable=self.minute_var, width=3,
                                     font=('Arial', 24, 'bold'), justify='center', relief='raised', bd=2)
        self.minute_entry.pack(side='left')
        self.minute_entry.bind('<FocusIn>', lambda e: self.select_part('minute'))
        self.minute_entry.bind('<KeyPress>', self.validate_minute_keypress)
        self.minute_entry.bind('<FocusOut>', self.validate_minute_input)

        # Space
        tk.Label(time_frame, text=" ", font=('Arial', 24)).pack(side='left')

        # Editable AM/PM entry
        self.ampm_entry = tk.Entry(time_frame, textvariable=self.ampm_var, width=3,
                                   font=('Arial', 20, 'bold'), justify='center', relief='raised', bd=2)
        self.ampm_entry.pack(side='left')
        self.ampm_entry.bind('<FocusIn>', lambda e: self.select_part('ampm'))
        self.ampm_entry.bind('<KeyPress>', self.validate_ampm_keypress)
        self.ampm_entry.bind('<KeyRelease>', self.validate_ampm_input)

        # Right increment/decrement buttons
        right_btn_frame = tk.Frame(time_container)
        right_btn_frame.pack(side='left', padx=1)

        self.inc_btn = tk.Button(right_btn_frame, text='▲', width=3, height=1,
                                 font=('Arial', 6, 'bold'), command=self.increase_time_part,
                                 bg='#E8F4FD', fg='#4A90E2', relief='raised', bd=2)
        self.inc_btn.pack(pady=2)

        self.dec_btn = tk.Button(right_btn_frame, text='▼', width=3, height=1,
                                 font=('Arial', 6, 'bold'), command=self.decrease_time_part,
                                 bg='#E8F4FD', fg='#4A90E2', relief='raised', bd=2)
        self.dec_btn.pack(pady=2)

        # Control buttons frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=20)

        self.start_btn = tk.Button(control_frame, text='🚀 Start Daily Shutdown', command=self.start_scheduler,
                                   font=('Arial', 12, 'bold'), bg='#4CAF50', fg='white',
                                   padx=20, pady=8, relief='raised', bd=3)
        self.start_btn.pack(side='left', padx=10)

        self.stop_btn = tk.Button(control_frame, text='⏹️ Stop Scheduler', command=self.stop_scheduler,
                                  font=('Arial', 12, 'bold'), bg='#F44336', fg='white',
                                  padx=20, pady=8, relief='raised', bd=3)
        self.stop_btn.pack(side='left', padx=10)

        # Countdown label
        self.countdown_label = tk.Label(self.root, text="Next shutdown: --:--:--",
                                        font=('Arial', 16, 'bold'), fg='#333',
                                        bg='#F0F0F0', relief='sunken', bd=2, pady=10)
        self.countdown_label.pack(pady=15, padx=20, fill='x')

        # Status label
        self.status_label = tk.Label(self.root, text="💡 Set time and start daily shutdown schedule",
                                     font=('Arial', 11), fg='green', wraplength=450)
        self.status_label.pack(pady=5)

    def perform_shutdown(self):
        """Execute shutdown command and show cancellation confirmation"""
        try:
            system = platform.system()

            if system == "Windows":
                # Cancel any existing shutdown first
                try:
                    subprocess.run(["shutdown", "/a"], check=False, timeout=10)
                except:
                    pass  # Ignore if no shutdown was scheduled

                # Schedule new shutdown
                delay = "30"
                msg = "Your PC will shut down in 30 seconds. Save your work."
                subprocess.run(["shutdown", "/s", "/t", delay, "/c", msg], check=True, timeout=30)

            elif system == "Linux":
                # Cancel existing and schedule new
                try:
                    subprocess.run(["shutdown", "-c"], check=False, timeout=10)
                except:
                    pass

                delay = "+1"
                msg = "Daily Shutdown"
                try:
                    subprocess.run(["shutdown", "-h", delay, msg], check=True, timeout=30)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    subprocess.run(["sudo", "shutdown", "-h", delay, msg], check=True, timeout=30)

            elif system == "Darwin":  # macOS
                try:
                    subprocess.run(["sudo", "shutdown", "-c"], check=False, timeout=10)
                except:
                    pass
                subprocess.run(["sudo", "shutdown", "-h", "+1"], check=True, timeout=30)

            if not self.headless_mode:
                self.status_label.config(text="✅ Shutdown command executed!", fg='orange')
                self.show_shutdown_confirmation()
            else:
                print("Shutdown command executed!")
                self.show_shutdown_confirmation()

        except Exception as e:
            error_msg = f"❌ Shutdown failed: {str(e)}"
            if not self.headless_mode:
                self.status_label.config(text=error_msg, fg='red')
            else:
                print(error_msg)

    def show_shutdown_confirmation(self):
        if self.headless_mode:
            try:
                # Create root window but keep it hidden
                root = tk.Tk()
                root.withdraw()

                # Show message box instead of custom popup
                result = messagebox.askyesno(
                    "Shutdown Confirmation",
                    "🛑 Shutdown in 30 seconds.\nDo you want to cancel?",
                    default='no'
                )

                if result:  # User clicked Yes (Cancel)
                    system = platform.system()
                    try:
                        if system == "Windows":
                            subprocess.run(["shutdown", "/a"], check=True)
                        elif system in ("Linux", "Darwin"):
                            subprocess.run(["shutdown", "-c"], check=True)
                        print("❌ Shutdown cancelled by user")
                    except Exception as e:
                        print(f"❌ Cancel failed: {e}")

                root.destroy()

            except Exception as e:
                print(f"Could not show popup: {e}")

            return

    def select_part(self, part):
        self.selected_part = part
        self.update_selection_highlight()

    def update_selection_highlight(self):
        self.hour_entry.config(bg=self.normal_bg, fg=self.normal_fg)
        self.minute_entry.config(bg=self.normal_bg, fg=self.normal_fg)
        self.ampm_entry.config(bg=self.normal_bg, fg=self.normal_fg)

    def validate_hour_keypress(self, event):
        if event.char.isdigit() or event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Tab']:
            return True
        return "break"

    def validate_minute_keypress(self, event):
        if event.char.isdigit() or event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Tab']:
            return True
        return "break"

    def validate_ampm_keypress(self, event):
        if event.char.upper() in 'APM' or event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Tab']:
            return True
        return "break"

    def validate_hour_input(self, event=None):
        try:
            value = self.hour_var.get()
            if not value:
                return
            if value.isdigit():
                hour = int(value)
                if 1 <= hour <= 12:
                    self.hour_var.set(f"{hour:02}")
                elif hour > 12:
                    if hour > 99:
                        self.hour_var.set("12")
                elif hour == 0:
                    self.hour_var.set("12")
        except ValueError:
            pass

    def validate_minute_input(self, event=None):
        try:
            value = self.minute_var.get()
            if not value:
                return
            if value.isdigit():
                minute = int(value)
                if 0 <= minute <= 59:
                    self.minute_var.set(f"{minute:02}")
                elif minute > 59:
                    if minute > 99:
                        self.minute_var.set("59")
        except ValueError:
            pass

    def validate_ampm_input(self, event=None):
        value = self.ampm_var.get().upper().strip()
        if not value:
            return
        if value in ['A', 'AM']:
            self.ampm_var.set('AM')
        elif value in ['P', 'PM']:
            self.ampm_var.set('PM')

    def increase_time_part(self):
        if self.selected_part == 'hour':
            hour = int(self.hour_var.get())
            hour = 1 if hour == 12 else hour + 1
            self.hour_var.set(f"{hour:02}")
        elif self.selected_part == 'minute':
            minute = int(self.minute_var.get())
            minute = (minute + 1) % 60
            self.minute_var.set(f"{minute:02}")
        elif self.selected_part == 'ampm':
            self.ampm_var.set('AM' if self.ampm_var.get() == 'PM' else 'PM')

    def decrease_time_part(self):
        if self.selected_part == 'hour':
            hour = int(self.hour_var.get())
            hour = 12 if hour == 1 else hour - 1
            self.hour_var.set(f"{hour:02}")
        elif self.selected_part == 'minute':
            minute = int(self.minute_var.get())
            minute = (minute - 1) % 60
            self.minute_var.set(f"{minute:02}")
        elif self.selected_part == 'ampm':
            self.ampm_var.set('AM' if self.ampm_var.get() == 'PM' else 'PM')

    def get_next_shutdown_datetime(self):
        now = datetime.now()

        if self.headless_mode:
            # In headless mode, use saved config values
            hour = int(self.saved_hour)
            minute = int(self.saved_minute)
            ampm = self.saved_ampm
        else:
            # In GUI mode, use current GUI values
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            ampm = self.ampm_var.get()

        if ampm == 'PM' and hour != 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0

        shutdown_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if shutdown_time <= now:
            shutdown_time += timedelta(days=1)
        return shutdown_time

    def countdown_loop(self):
        while not self.stop_thread.is_set():
            now = datetime.now()
            diff = self.shutdown_time - now

            if diff.total_seconds() <= 0:
                self.countdown_label.config(text="🔴 SHUTTING DOWN NOW...")
                self.status_label.config(text="Daily shutdown triggered! Computer will restart tomorrow.", fg='red')
                self.perform_shutdown()
                if self.daily_mode and not self.stop_thread.is_set():
                    self.schedule_next_day()
                return
            else:
                hours, remainder = divmod(int(diff.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                self.countdown_label.config(text=f"⏰ Next shutdown: {hours:02d}:{minutes:02d}:{seconds:02d}")
            time.sleep(1)

    def log_scheduler_action(self, action):
        log_file = "shutdown_log.csv"
        file_exists = os.path.isfile(log_file)

        with open(log_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Timestamp", "Action", "Scheduled Time"])

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            scheduled_time = self.shutdown_time.strftime("%I:%M %p") if self.shutdown_time else "N/A"
            writer.writerow([timestamp, action, scheduled_time])

    def schedule_next_day(self):
        if not self.stop_thread.is_set():
            time.sleep(2)
            self.shutdown_time = self.get_next_shutdown_datetime()

            if not self.headless_mode:
                self.status_label.config(
                    text=f"✅ Daily shutdown rescheduled for {self.shutdown_time.strftime('%I:%M %p')} tomorrow",
                    fg='green')
                self.countdown_loop()
            else:
                print(f"Rescheduled for tomorrow at {self.shutdown_time.strftime('%I:%M %p')}")
                self.headless_countdown_loop()

    def start_scheduler(self):
        if not self.hour_var.get() or not self.minute_var.get() or not self.ampm_var.get():
            self.status_label.config(text="❌ Please fill in all time fields!", fg='red')
            return

        confirm = self.show_confirmation_dialog(
            "Start Scheduler",
            "Are you sure you want to schedule daily shutdown at the selected time?",
            yes_text="Yes, Start", no_text="Cancel"
        )
        if not confirm:
            return

        if self.is_scheduler_running:
            self.stop_scheduler()

        self.save_config()
        self.shutdown_time = self.get_next_shutdown_datetime()
        self.status_label.config(
            text=f"✅ Daily shutdown scheduled for {self.shutdown_time.strftime('%I:%M %p')} every day",
            fg='green')
        self.stop_thread.clear()
        self.is_scheduler_running = True
        self.timer_thread = threading.Thread(target=self.countdown_loop, daemon=True)
        self.timer_thread.start()
        self.log_scheduler_action("Daily Shutdown Scheduled")

    def stop_scheduler(self):
        confirm = self.show_confirmation_dialog(
            "Stop Scheduler",
            "Are you sure you want to stop the daily shutdown schedule?",
            yes_text="Yes, Stop", no_text="Cancel"
        )
        if not confirm:
            return

        self.stop_thread.set()
        self.is_scheduler_running = False
        self.countdown_label.config(text="⏸️ Scheduler stopped")
        self.status_label.config(text="⏹️ Daily shutdown schedule stopped.", fg='orange')
        self.log_scheduler_action("Daily shutdown schedule stopped")

    def show_confirmation_dialog(self, title, message, yes_text="Yes", no_text="No", show_scheduled_time=False):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        result = [False]

        # Create message label
        tk.Label(dialog, text=message, font=("Arial", 11), justify="center").pack(pady=10)

        # Optional: Show scheduled time
        if show_scheduled_time and self.shutdown_time:
            formatted_time = self.shutdown_time.strftime("%I:%M %p")
            tk.Label(dialog, text=f"Current scheduled time: {formatted_time}",
                     font=("Arial", 10), fg="gray").pack()

        # Button frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=15)

        def confirm():
            result[0] = True
            dialog.destroy()

        def cancel():
            result[0] = False
            dialog.destroy()

        tk.Button(button_frame, text=yes_text, command=confirm, bg="#4CAF50", fg="white", padx=15).pack(side="left",
                                                                                                        padx=10)
        tk.Button(button_frame, text=no_text, command=cancel, bg="#F44336", fg="white", padx=15).pack(side="left",
                                                                                                      padx=10)

        # Center the dialog relative to the root window
        dialog.update_idletasks()
        w = dialog.winfo_width()
        h = dialog.winfo_height()
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (w // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        dialog.wait_window(dialog)
        return result[0]


def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description='Power E Shutdown Scheduler')
    parser.add_argument('--head', action='store_true',
                        help='Run in GUI mode (with interface)')
    parser.add_argument('--settings', action='store_true',
                        help='Run in GUI settings mode (launched from batch file)')

    args = parser.parse_args()

    if args.head or args.settings:
        # GUI mode (with --head or --settings argument)
        root = tk.Tk()
        app = ShutdownScheduler(root, headless_mode=False)
        root.mainloop()
    else:
        # Headless mode (default)
        app = ShutdownScheduler(headless_mode=True)


if __name__ == "__main__":
    main()