import asyncio

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from globals_and_settings import EAction
from logger import info, warning


class ControllerTaskQ(QObject):
    qts_manage_monitoring = pyqtSignal(EAction)
    qts_visualize_data = pyqtSignal(dict)

    def __init__(self, model_monitoring, view):
        super().__init__()
        self.model = model_monitoring
        self.view = view
        self.signal_slot_setup()

    # noinspection PyUnresolvedReferences
    def signal_slot_setup(self):
        """Qt Signals, Events, Slots, Actions setup"""
        self.qts_manage_monitoring.connect(self.pass_slot)              # Controller's
        self.model.qts_data_changed.connect(self.pass_slot)             # Model's
        self.qts_visualize_data.connect(self.pass_slot)                 # Controller's
        self.view.qts_user_condocopymove.connect(self.pass_slot)        # View's
        self.model.qts_exception_condocopymove.connect(self.pass_slot)  # Model's
        self.model.qts_state_condocopymove.connect(self.pass_slot)      # Model's

    async def run_monitoring(self):
        while True:
            await asyncio.sleep(5)
            self.model.update_data({'data': "Data from monitoring task"})

    async def run_view(self):
        self.view.show()

    async def run_user_logging(self):
        while True:
            await asyncio.sleep(10)
            info(f"Logging: {self.model.get_data()}")

    async def run_condocopymove(self):
        pass

    @pyqtSlot()
    def on_shutdown(self):
        info("Shutting down...")

    def pass_slot(self, *args, **kwargs):
        """Service dev slot"""
        pass
