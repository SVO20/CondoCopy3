from PyQt5.QtCore import QObject, pyqtSignal


class MonitoringTaskQ(QObject):
    qts_data_changed = pyqtSignal(dict)
    qts_exception_condocopymove = pyqtSignal()
    qts_state_condocopymove = pyqtSignal()


    def __init__(self):
        super().__init__()
        self._data = {}

    def update_data(self, new_data: dict):
        self._data = new_data
        self.qts_data_changed.emit(self._data)

    def get_data(self):
        return self._data

