"""
Module provides a system tray application that monitors SD card insertion
and analyzes the SD card structure.

"""

import asyncio
import os
import sys
import zlib
from collections import deque

import psutil
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import (QApplication, QDialog, QLabel, QMenu, QPushButton, QSystemTrayIcon,
                             QVBoxLayout, QAction)

from logger import debug, error, info, omit, success, trace, warning
from take10 import get_volume_info_kernel32, get_folder_creation_date


# deque_removables format --v
# deque([{'device': str(drive), 'id': str(drive_id)}, ... ])
deque_removables = deque()


async def get_removable_drives() -> list:
    partitions = psutil.disk_partitions()
    removable_drives = [p.device for p in partitions if 'removable' in p.opts]
    return removable_drives


def generate_id(drive):
    """Generates a unique ID for a drive based on its volume information and
     creation dates of specific folders (if presented on drive and available to retrieve).

    The ID is constructed using the following steps:
    1. Get volume label, volume serial number, and total size of the drive
    2. Get the distinst folders creation dates ("" if there is no folder on the drive) and
        concat into a single string
    3. Concat the volume label, volume serial number, total size, and folder creation dates
        into a single string
    4. Calculate the CRC32 checksum of the combined string
    5. Use the first six characters of the CRC32 checksum (in uppercase) as a suffix for the ID
    6. Compose the final ID in the format "VOLUME_LABEL_HASH_SUFFIX".
    """

    # Folders which creation dates to be used as unique marks  (if exists and available)
    distinst_folders = ("DCIM", "MISC", "Android")

    volume_label, volume_serial, total_size = get_volume_info_kernel32(drive)
    str_creation_dates = "".join([get_folder_creation_date(os.path.join(drive, folder))
                                  for folder in distinst_folders])

    # Create the string to be hashed and calculate its CRC32 checksum
    combined_str = f"{volume_label}{volume_serial}{total_size}{str_creation_dates}"
    crc32_hash = zlib.crc32(combined_str.encode())
    # use six first chars
    hash_suffix = f"{crc32_hash:08x}"[:6].upper()

    # compose and return ID
    return f"{volume_label}_{hash_suffix}"


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
            # v-- non-blocking --v
            self.menu.popup(QCursor.pos())

    async def on_sd_inserted(self, drive):
        await self.analyze_sd_card(drive)
        self.notify_user(f"SD card analyzed: {drive}")
        info(f"SD card analyzed: {drive}")

        # Показать окно с кнопками
        dialog = SDCardDialog(drive)
        dialog.exec_()

    async def analyze_sd_card(self, drive_path):
        # Здесь можно выполнить длительную операцию по анализу SD карты
        await asyncio.sleep(1)

    def notify_user(self, message):
        pass


if __name__ == "__main__":
    tray_app = TrayApp()
    tray_app.run()
