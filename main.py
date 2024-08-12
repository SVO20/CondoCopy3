import asyncio
import sys

from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

from globals_and_settings import settings
from controller import ControllerTaskQ
from model import MonitoringTaskQ
from view import ProgramViewQ


async def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    model_monitoring = MonitoringTaskQ()
    view = ProgramViewQ()
    controller = ControllerTaskQ(model_monitoring, view)

    # Connect core signal triggered by QApplication.quit() with  on_shutdown slot
    app.aboutToQuit.connect(controller.on_shutdown)

    await asyncio.gather(controller.run_monitoring(),
                         controller.run_view(),
                         controller.run_user_logging() if settings.take.user_level_logging
                         else asyncio.sleep(0))


if __name__ == "__main__":
    asyncio.run(main())
