import asyncio
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

from controller import ControllerTaskQ
from globals_and_settings import settings
from model import MonitoringTaskQ
from view import ProgramViewQ


async def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    model_monitoring = MonitoringTaskQ()
    view = ProgramViewQ()
    controller = ControllerTaskQ(model_monitoring, view)

    # Connect core signal triggered by QApplication.quit() with on_shutdown slot
    app.aboutToQuit.connect(controller.on_shutdown)

    async def run_tasks():
        """Schedule asyncio tasks"""
        await asyncio.create_task(controller.run_monitoring())
        if settings.take.user_level_logging:
            await asyncio.create_task(controller.run_user_logging())

    # to the end of the Qt loop
    QTimer.singleShot(0, lambda: asyncio.create_task(run_tasks()))

    # Launch the Qt own events -> Run UI -> run_tasks()
    app.exec_()


if __name__ == "__main__":
    asyncio.run(main())
