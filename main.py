"""
CondoCopy3 v0.0


"""
import asyncio
import os
import sys
import zlib
from collections import deque

from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QLabel, QMenu,
                             QPushButton, QSystemTrayIcon, QVBoxLayout)

from detectors import get_removable_drives, generate_id, match_camera_model
from initialization import d_cameras
from logger import debug, error, info, omit, success, trace, warning


# deque_removables format --v
# deque([{'device': str(drive), 'id': str(drive_id)}, ... ])
deque_removables = deque()


class SDCardDialog(QDialog):
    def __init__(self, drive, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SD Card Inserted")
        self.drive = drive
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        message = QLabel(f"SD card inserted: {self.drive}")
        layout.addWidget(message)

        button_ok = QPushButton("OK")
        button_ok.clicked.connect(self.accept)
        layout.addWidget(button_ok)

        self.setLayout(layout)


class TrayApp:
    def __init__(self):
        # Initialize the QApplication
        self.parent_app_ = QApplication(sys.argv)

        # === TRAY ===
        # Create a system tray icon as child
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
        self._loop = asyncio.get_event_loop()
        # Create a flag to ensure the Qt app is alive
        self.running = True

        ## === VARS ===
        self.last_drive_list = []

    def run(self):
        # Schedule the SD card monitoring task
        self._loop.create_task(self.monitor_sd_insertion(self.on_sd_inserted))
        # Run the Qt application and asyncio event loop together
        self._loop.run_until_complete(self.qt_life_cycle())

    async def update_drives(self):
        set_current_removables = set(await get_removable_drives())
        set_deque_removables = {drive['device'] for drive in deque_removables}
        updated = False

        # Add new drives
        for drive in set_current_removables - set_deque_removables:
            drive_id = generate_id(drive)

            camera_model = match_camera_model(drive, d_cameras)
            success(f"The SD card is matched with: {camera_model}")
            # todo add camera_model to deque_removables

            # deque_removables format --v
            # deque([{'device': str(drive), 'id': str(drive_id)}, ... ])
            deque_removables.append({'device': drive, 'id': drive_id})
            updated = True

        # Remove disconnected drives
        for drive in list(deque_removables):
            if drive['device'] not in set_current_removables:
                deque_removables.remove(drive)
                updated = True

        return updated

    async def refresh_display(self, deque_removables):
        # todo Refresh window state/content
        pass

    async def monitor_sd_insertion(self, callback):
        while True:
            updated = await self.update_drives(self.deque_removables)
            if updated:
                await self.refresh_display(self.deque_removables)
            await asyncio.sleep(1)

            # Wait for 2 seconds
            await asyncio.sleep(2)

    async def qt_life_cycle(self):
        # Run the Qt application intertnal events until the application quits
        debug(f"Qt application to run")
        while self.running:
            self.parent_app_.processEvents()
            await asyncio.sleep(0.1)

    def exit(self):
        # Hide the tray icon and quit the application
        self.tray_icon.hide()
        self.parent_app_.quit()
        # Stop the app
        self.running = False

    ### ----------------------------------------------------------------------

    def on_tray_icon_activated(self, reason):
        # Left click handling
        if reason == QSystemTrayIcon.Trigger:
            self.menu.popup(QCursor.pos())

    async def on_sd_inserted(self, drive):
        await self.analyze_sd_card(drive)
        self.notify_user(f"SD card analyzed: {drive}")
        info(f"SD card analyzed: {drive}")

        # Show dialog window
        dialog = SDCardDialog(drive)
        # v-- BLOCKING! --v
        dialog.exec_()

    async def analyze_sd_card(self, drive_path):
        # placeholder for analyze
        await asyncio.sleep(1)

    def notify_user(self, message):
        pass


if __name__ == "__main__":
    tray_app = TrayApp()
    tray_app.run()
