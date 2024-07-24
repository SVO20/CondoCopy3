import sys
import asyncio
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QDialog, QVBoxLayout, QLabel, QPushButton
from qasync import QEventLoop, asyncSlot

from initialization import d_cameras
from logger import debug
from models import RemovablesModel
from views import SDCardDialog


class TrayAppController:
    def __init__(self, parent_app, model):
        self.model = model
        self._parent_app = parent_app

        self.tray_icon = QSystemTrayIcon(QIcon("icon1.png"), self._parent_app)

        # Create actions for the tray icon menu
        action_about = QAction(QIcon('about.png'), "About", self.tray_icon)
        action_about.triggered.connect(self.on_action_about)

        action_quit = QAction(QIcon('exit.png'), "Quit", self.tray_icon)
        action_quit.triggered.connect(self.on_action_quit)

        # Create the tray icon menu
        self.menu = QMenu()
        self.menu.addAction(action_about)
        self.menu.addAction(action_quit)

        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()

    async def start_monitoring(self):
        # Start monitoring removable devices
        await self.model.do_monitor_removables()

    async def qt_life_cycle(self):
        # Run the Qt application internal events until the application quits
        debug("Qt application to run")
        while True:
            self._parent_app.processEvents()
            await asyncio.sleep(0.1)

    @asyncSlot()
    async def refresh_display(self):
        # Refresh the display with currently connected devices
        devices = self.model.get_devices()
        for device in devices:
            dialog = SDCardDialog(device['device'])
            dialog.setWindowModality(Qt.NonModal)
            dialog.show()

    def on_action_quit(self):
        self.tray_icon.hide()
        self._parent_app.quit()

    def on_action_about(self):
        # Show about window (implementation needed)
        pass

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.menu.popup(QCursor.pos())


async def main():
    # QApplication, QEventLoop
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    model = RemovablesModel(d_cameras)
    controller_trayapp = TrayAppController(app, model)

    # Schedule the monitoring task
    await asyncio.create_task(controller_trayapp.start_monitoring())
    # Run the Qt application and asyncio event loop together
    await asyncio.create_task(controller_trayapp.qt_life_cycle())

    with loop:
        await loop.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
