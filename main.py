"""
CondoCopy3 v0.0

"""
import asyncio
import sys
from collections import deque

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QLabel, QMenu,
                             QPushButton, QSystemTrayIcon, QVBoxLayout)

from logger import debug, error, info, omit, success, trace, warning
from my_utils import get_removable_drives, generate_id
from match_camera import match_camera_model

from settings import d_cameras, settings


# deque_removables format --v
# deque([{'device': str(drive), 'id': str(drive_id)}, ... ])
deque_removables = deque()


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
        # Schedule the monitoring task
        self._loop.create_task(self.monitor_removables_atask())
        # Run the Qt application and asyncio event loop together
        self._loop.run_until_complete(self.qt_life_cycle_atask())

    async def monitor_removables_atask(self):
        while True:
            # detect current
            set_current_removables = set(await get_removable_drives())
            # retrieve last
            set_last_removables = {drive['device'] for drive in deque_removables}
            # suppose no changes
            is_updated = False

            # Check for new connected removables
            for drive in set_current_removables - set_last_removables:
                drive_id = generate_id(drive)
                camera_model = match_camera_model(drive, d_cameras)

                # todo add camera_model to deque_removables

                # deque_removables format --v
                # deque([{'device': str(drive), 'id': str(drive_id)}, ... ])
                deque_removables.append({'device': drive, 'id': drive_id})

                success(f"The removable is matched with: {camera_model}")
                is_updated = True

            # Check for disconnected drives
            for drive in list(deque_removables):
                if drive['device'] not in set_current_removables:
                    deque_removables.remove(drive)
                    success(f"The removable [{drive['id']}] was disconnected")
                    is_updated = True

            # Handle changes in  deque_removables
            trace(f"{deque_removables = }")
            if is_updated:
                await self.refresh_display_atask()

            await asyncio.sleep(1)

    async def qt_life_cycle_atask(self):
        # Run the Qt application intertnal events until the application quits
        debug(f"Qt application to run")
        while self.running:
            self.parent_app_.processEvents()
            await asyncio.sleep(0.1)

    async def refresh_display_atask(self):
        # Show dialog window

        # placeholder for display logic
        # todo display logic
        #
        # kinda    -->     f"{drive['device']} (Removable) ID: {drive['id']}"
        dialog = SDCardDialog('A:')
        dialog.setWindowModality(Qt.NonModal)
        dialog.show()

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


if __name__ == "__main__":
    tray_app = TrayApp()
    tray_app.run()
