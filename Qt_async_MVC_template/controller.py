from PyQt5.QtCore import QObject, pyqtSlot


class ControllerTask(QObject):
    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view
        self.connect_signals()

    def connect_signals(self):
        self.model.data_updated.connect(self.view.update_label)

        self.view.button_clicked.connect(self.on_button_clicked)
        self.view.pause_clicked.connect(self.model.pause)
        self.view.resume_clicked.connect(self.model.resume)

    async def start_model_worker(self):
        self.model.start()

    async def run_view(self):
        self.view.show()

    async def shutdown(self):
        await self.model.stop()

    @pyqtSlot()
    def on_button_clicked(self):
        print("Button clicked")
