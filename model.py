from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

from globals_and_settings import Action
from logger import warning, info, trace


class MonitoringTaskQ(QObject):
    """Manage monitoring task and handle actions"""

    qts_data_changed = pyqtSignal(dict)
    qts_exception_condocopymove = pyqtSignal()
    qts_state_condocopymove = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.mon_qthread = MonThreadQ()  # <-- ensure mon_qthread is of type MonThreadQ()

        self._data = {}

    @pyqtSlot()
    def manage_mon(self, action: Action):
        match action:
            case Action.RESTART:
                # Forced stop implementation
                if self.mon_qthread.isRunning():
                    # Running thread stopping
                    self.mon_qthread.stop()
                    if self.mon_qthread.wait(100):
                        trace(f"The MonThreadQ thread safely interrupted")
                        # thread interrupted - OK
                    else:
                        warning(f"Unsafe interruption of the MonThreadQ thread!")
                        self.mon_qthread.terminate()
                        self.mon_qthread.wait()
                        # thread interrupted - NOT OK

                # Stopped, interrupted or never been started thread
                self.mon_qthread = MonThreadQ()  # <-- new MonThreadQ() instance
                self.mon_qthread.start()
                info(f"Monitoring thread started successfully")
            case Action.PAUSE:
                self.mon_qthread.pause()
            case Action.RESUME:
                self.mon_qthread.resume()
            case Action.STOP:
                self.mon_qthread.stop()
            case _:
                raise ValueError(f"Unknown action: {action}")

    def update_data(self, new_data: dict):
        self._data = new_data
        self.qts_data_changed.emit(self._data)

    def get_data(self):
        return self._data


# ========================

class MonThreadQ(QThread):
    """Thread for monitoring task"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._paused = False

    def run(self):
        while not self.isInterruptionRequested():  # Check if interruption needed
            while self._paused:  # Check if paused
                if self.isInterruptionRequested():  # Avoid interruption miss when paused
                    return
                QThread.msleep(100)  # Avoid busy

            # V-- Thread routine --V

            info("Monitoring...")
            QThread.sleep(1)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def stop(self):
        self.requestInterruption()
