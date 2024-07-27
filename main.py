import sys
import asyncio
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QWidget
from qasync import QEventLoop  # , asyncSlot

from initialization import d_cameras
from logger import debug, trace
from models import RemovablesModel
from views import SDCardDialog


class MainInvisibleParent(QWidget):
    def __init__(self, model, view):
        super().__init__()

        self.setWindowTitle("Invisible Parent Entity Controller")   # Controller
        self.setWindowFlags(self.windowFlags() | Qt.Tool)           # Tool window !!
        self.hide()                                                 # Hidden window !!

        # Init model
        self.model = model
        # Init view
        self.view = view

        # Create TrayIcon
        self.tray_icon = QSystemTrayIcon(QIcon("icon1.png"), self)
        self.tray_icon.setToolTip("CondoCopy3")

        # Create app actions
        self._create_app_actions()

        # Create tray menu
        self.tray_menu = QMenu(self)
        self.tray_menu.addAction(self.action_about)
        self.tray_menu.addAction(self.action_quit)
        self.tray_icon.setContextMenu(self.tray_menu)

        # 'Run' tray icon
        self.tray_icon.show()

    def _create_app_actions(self):
        # Create actions for the tray icon menu
        self.action_about = QAction(QIcon('about.png'), "About", self.tray_icon)
        self.action_about.triggered.connect(self.on_action_about)
        self.action_quit = QAction(QIcon('exit.png'), "Quit", self.tray_icon)
        self.action_quit.triggered.connect(self.on_action_quit)
        # Left click for tray menu handling
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Connect the model signal to the refresh_display slot
        self.model.qts_removables_changed.connect(self.on_model_refresh)

    def on_action_about(self):
        # Show about window (implementation needed)
        pass

    def on_action_quit(self):
        self.model.stop()
        self.tray_icon.hide()
        self._parent_app.quit()

    def on_model_refresh(self):
        # Refresh the display with currently connected devices
        devices = self.model.current_removables()

        SDCardDialog.singleton_instance(devices, self)

        # trace(f"microservice <-- to run")
        # asyncio.create_task(self.microservice())
        # trace(f"microservice scheduled OK")

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.menu.popup(QCursor.pos())

    async def microservice(self):
        # test
        trace(f"test microservice ON")
        await asyncio.sleep(10)
        trace(f"test microservice OFF")

    async def start_monitoring(self):
        # ASYNC Start monitoring removable devices
        await self.model.do_monitor_removables()

    async def qt_life_cycle(self):
        # ASYNC Run the Qt application internal events until the application quits
        debug("Qt application to run")
        while True:
            self._parent_app.processEvents()
            await asyncio.sleep(0.1)
# -----------------------------------------------------------------------------------------------


async def main():
    # QApplication, QEventLoop
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Qevent

    model = RemovablesModel(d_cameras)
    view = SDCardDialog.singleton_instance()
    controller_parent_vindow = MainInvisibleParent(model, view)

    # Schedule the monitoring task
    await asyncio.create_task(controller_parent_vindow.start_monitoring())
    # Run the Qt application and asyncio event loop together
    await asyncio.create_task(controller_parent_vindow.qt_life_cycle())

    with loop:
        await loop.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
