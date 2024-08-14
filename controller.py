import asyncio
from enum import Enum
from typing import Optional, Any

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from globals_and_settings import Action, CCAction, UserAction
from logger import info, warning, error


class ControllerTaskQ(QObject):
    qts_do_manage_mon = pyqtSignal(Action)
    qts_do_visualize_data = pyqtSignal(Optional[Any])
    qts_do_condocopy = pyqtSignal(CCAction, Optional[Any])

    def __init__(self, model_manager, view):
        super().__init__()
        self.model = model_manager
        self.view = view
        self.signal_slot_setup()

    # noinspection PyUnresolvedReferences
    def signal_slot_setup(self):
        """Qt Signals, Events, Slots, Actions setup"""
        self.qts_do_manage_mon.connect(self.model.manage_mon)           # Controller's
        self.qts_do_visualize_data.connect(self.view.on_visualize_req)  # Controller's
        self.qts_do_condocopy.connect(self.model.manage_condocopy)      # Controller's

        self.model.qts_data_changed.connect(self.on_removables_changed)                 # Model's
        self.model.qts_exception_condocopy.connect(self.condocopy_exception_handle)     # Model's
        self.model.qts_state_condocopy.connect(self.condocopy_state_handle)             # Model's

        self.view.qts_user_action.connect(self.on_user_activity)                    # View's
        self.view.mon_indic.qts_user_force_monstate.connect(self.on_user_activity)  # View's

    async def run_monitoring(self):
        while True:
            self.model.update_data({'data': "Data from monitoring task"})
            await asyncio.sleep(5)

    async def run_user_logging(self):
        while True:
            info(f"Logging: {self.model.get_data()}")
            await asyncio.sleep(10)

    async def run_condocopymove(self):
        pass

    @pyqtSlot()
    def before_shutdown(self):
        info("Shutting down...")

    @pyqtSlot()
    def pass_slot(self, *args, **kwargs):
        """Service dev slot"""
        pass

    @pyqtSlot()
    def condocopy_exception_handle(self, e: Exception):
        error(f"CondoCopy exception occured {e=}")
        raise e

    @pyqtSlot()
    def condocopy_state_handle(self, data=None):
        pass

    @pyqtSlot()
    def on_user_activity(self, user_action: Enum, opt_args=None):
        match user_action:
            case UserAction.PAUSE_MON:
                pass
            case UserAction.RESUME_MON:
                pass
            case UserAction.PAUSE_MON:
                pass
            case UserAction.CCOPY_ALL:
                pass
            case UserAction.CMOVE_ALL:
                pass
            case UserAction.CSIMULATE_ALL:
                pass
            case UserAction.CRENAME_LIST:
                if opt_args is None:
                    raise ValueError("CRENAME_LIST requires additional arguments.")
                pass
            case _:
                raise ValueError(f"Unknown user action: {user_action}")
