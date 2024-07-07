import sys
import os
import asyncio
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QCursor
import win32file
import datetime

class TrayApp:
    def __init__(self):
        # Initialize the QApplication
        self.parent_app_ = QApplication(sys.argv)

        # === TRAY ===
        # Create a system tray icon as child of QApplication instance
        self.tray_icon = QSystemTrayIcon(QIcon("icon1.png"), self.parent_app_)
        # Create a context menu
        self.menu = QMenu()
        self.action_quit = QAction("Quit")
        self.action_quit.triggered.connect(self.exit)
        self.menu.addAction(self.action_quit)
        # Set the context menu for the tray icon
        self.tray_icon.setContextMenu(self.menu)
        # Left click for tray menu handling
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        # Show the tray icon
        self.tray_icon.show()

        ## === ASYNC LOOP ===
        # Initialize the asyncio event loop
        self.loop_ = asyncio.get_event_loop()
        # Create a flag to ensure the Qt app is alive
        self.running = True

    def run(self):
        # Schedule the SD card monitoring task
        self.loop_.create_task(self.monitor_sd_insertion(self.on_sd_inserted))
        # Run the Qt application and asyncio event loop together
        self.loop_.run_until_complete(self.qt_life_cycle())

    async def monitor_sd_insertion(self, callback):
        # Get a list of removable drives (SD cards)
        drive_list = ['%c:\\' % d for d in range(65, 91) if
                      win32file.GetDriveType('%c:\\' % d) == win32file.DRIVE_REMOVABLE]
        while self.running:
            # Print a debug message to indicate the task is running
            print("Async task running...")
            # Check each drive to see if it exists and has a volume
            for drive in drive_list:
                if os.path.exists(drive) and win32file.GetVolumeInformation(drive):
                    # If a drive is found, call the provided callback function
                    callback(drive)
            # Wait for 1 second before checking again
            await asyncio.sleep(1)

    async def qt_life_cycle(self):
        # Run the Qt application intertnal events until the application quits
        while self.running:
            self.parent_app_.processEvents()
            await asyncio.sleep(0.1)

    def exit(self):
        # Hide the tray icon and quit the application
        self.tray_icon.hide()
        self.parent_app_.quit()
        # Stop the app
        self.running = False

    def on_sd_inserted(self, drive):
        # Analyze the SD card and notify the user
        analyze_sd_card(drive)
        notify_user(f"SD card analyzed: {drive}")
        log_event("INFO", f"SD card analyzed: {drive}")

    ### ----------------------------------------------------------------------

    def on_tray_icon_activated(self, reason):
        # Left click handling
        if reason == QSystemTrayIcon.Trigger:
            self.menu.exec_(QCursor.pos())

def analyze_sd_card(drive_path):
    # Define the required structure of folders and files on the SD card
    required_structure = ["folder1", "folder2", "file1.txt"]
    found_items = []

    # Walk through the drive path and check for required folders and files
    for root, dirs, files in os.walk(drive_path):
        for name in dirs + files:
            if name in required_structure:
                found_items.append(name)

    # Check if the required structure is present
    if set(required_structure).issubset(set(found_items)):
        print("Required structure found.")
        # Trigger notification and logging here
    else:
        print("Required structure not found.")

def notify_user(message):
    # Placeholder for actual notification code
    print(f"Notification: {message}")

def log_event(event_type, message):
    # Append the event log with a timestamp and message
    with open("event_log.txt", "a") as log_file:
        log_file.write(f"{datetime.datetime.now()} - {event_type}: {message}\n")

if __name__ == "__main__":
    # Create an instance of TrayApp and run it
    tray_app = TrayApp()
    tray_app.run()
