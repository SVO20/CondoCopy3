from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

from globals_and_settings import Action
from logger import warning, info


class MonThreadQ(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._paused = False

    def run(self):
        while not self.isInterruptionRequested():           # Check if interruption needed
            while self._paused:                             # Check if paused
                while not self.isInterruptionRequested():   # Avoid interruption miss
                    QThread.msleep(100)                     # Avoid busy

            # V-- Thread routine --V

            print("Working...")
            QThread.sleep(1)

    def pause(self):
        self._paused = True

    def resume(self):
        pass

    def stop(self):
        self.requestInterruption()



class MonitoringTaskQ(QObject):
    qts_data_changed = pyqtSignal(dict)
    qts_exception_condocopymove = pyqtSignal()
    qts_state_condocopymove = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.mon_qthread = MonThreadQ()  # <-- ensure mon_qthread is of type MonThreadQ()

        self._data = {}

    def update_data(self, new_data: dict):
        self._data = new_data
        self.qts_data_changed.emit(self._data)

    def get_data(self):
        return self._data

    @pyqtSlot()
    def manage_mon(self, action: Action):
        match action:
            case Action.RESTART:
                if self.mon_qthread.isRunning():
                    # Running thread stopping
                    self.mon_qthread.stop()
                    if self.mon_qthread.wait(100):
                        pass
                        # thread interrupted - OK
                    else:
                        warning(f"Unsafe monitoring thread interruption!")
                        self.mon_qthread.terminate()
                        self.mon_qthread.wait()
                        # thread interrupted - NOT OK
                # Stopped, interrupted or never been started thread
                self.mon_qthread = MonThreadQ()  # <-- new MonThreadQ() instance
                self.mon_qthread.start()
                info(f"Monitoring thread started successfully")
            case Action.PAUSE:
                pass
            case Action.RESUME:
                pass
            case Action.STOP:
                pass
            case _:
                raise ValueError(f"Unknown action: {action}")
