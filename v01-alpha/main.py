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
from initialization import d_cameras
from detectors import get_removable_drives, generate_id, match_camera_model

from qasync import QEventLoop, asyncSlot

# deque_removables format --v
# deque([{'device': str(drive), 'id': str(drive_id)}, ... ])
deque_removables = deque()


class TrayApp:
    def __init__(self, parent_app):
        self._parent_app = parent_app

        # === TRAY ===
        # Create a system tray icon
        self.tray_icon = QSystemTrayIcon(QIcon("icon1.png"), self._parent_app)

        # Create QActions
        action_about = QAction(QIcon('about.png'), "About", self.tray_icon)
        action_about.triggered.connect(self.on_action_about)

        action_quit = QAction(QIcon('exit.png'), "Quit", self.tray_icon)
        action_quit.triggered.connect(self.on_action_quit)

        # Create a tray menu
        self.menu = QMenu()
        self.menu.addAction(action_about)
        self.menu.addAction(action_quit)



        # Show the tray icon
        self.tray_icon.show()

        ## === VARS ===
        self.last_drive_list = []

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
        while True:
            self._parent_app.processEvents()
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

    def on_action_quit(self):
        # Hide the tray icon and quit the application
        self.tray_icon.hide()
        self._parent_app.quit()

    def on_action_about(self):
        # Show about window
        # todo show About window
        pass

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


async def main():
    # QApplication, QEventLoop
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    #
    asyncio.set_event_loop(loop)

    tray_app = TrayApp(app)
    # Schedule the monitoring task
    await asyncio.create_task(tray_app.monitor_removables_atask())
    # Run the Qt application and asyncio event loop together
    await asyncio.create_task(tray_app.qt_life_cycle_atask())

    with loop:
        await loop.run_forever()

if __name__ == "__main__":
    asyncio.run(main())


