import builtins
import random

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QMutexLocker

from logger import debug


class TempModelWorker(QThread):
    worker_data_updated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.paused = False

    def run(self):
        while self.running:
            while self.paused:  # Check if paused
                QThread.msleep(100)  # Short sleep to avoid busy waiting
            n = random.randint(10, 40)
            fib_n = self.fibonacci(n)
            self.worker_data_updated.emit(f"Fibonacci({n}) = {fib_n}")
            QThread.msleep(1)

    def fibonacci(self, n):
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    def stop(self):
        self.running = False

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False


class TempModel(QObject):
    data_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.worker = TempModelWorker()
        self.worker.worker_data_updated.connect(self.data_updated.emit)

    def start(self):
        debug(f"Worker to start")
        self.worker.start()
        debug(f"Worker started succesful")

    def stop(self):
        self.worker.stop()
        self.worker.wait()

    @pyqtSlot()
    def pause(self):
        self.worker.pause()

    @pyqtSlot()
    def resume(self):
        self.worker.resume()
