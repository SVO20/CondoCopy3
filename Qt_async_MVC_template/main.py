import asyncio
import sys

from PyQt5.QtCore import QMutex
from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

from controller import ControllerTask
from model import TempModel
from view import TempView


async def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    model = TempModel()
    view = TempView()
    controller = ControllerTask(model, view)

    try:
        await asyncio.gather(controller.start_model_worker(),
                             controller.run_view())
    except (KeyboardInterrupt, SystemExit):
        await controller.shutdown()

    with loop:
        await loop.run_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
