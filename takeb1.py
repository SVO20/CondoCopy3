from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QApplication, QWidget
from PyQt5.QtCore import Qt
import sys
import asyncio
from qasync import QEventLoop, asyncSlot


class RemovablesView(QWidget):
    """Info window"""

    _instance = None  # SINGLETON instance

    @classmethod
    def singleton_instance(cls, parent=None):
        if cls._instance is None:
            cls._instance = RemovablesView(parent)
        return cls._instance

    def __new__(cls, parent=None):
        if cls._instance is None:
            cls._instance = super(RemovablesView, cls).__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        # to be run once
        super().__init__(parent)
        self.setWindowTitle("Removable inserted")
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.device_qlabels = []
        self.layout = QVBoxLayout()
        self.message = QLabel()
        self.layout.addWidget(self.message)
        self.button_close = QPushButton("Close")
        self.button_close.clicked.connect(self.close)
        self.layout.addWidget(self.button_close)
        self.setLayout(self.layout)

        self.devices = []

        self.lower_down()

    async def update_content(self, devices):
        if not devices:
            self.lower_down()
            return
        self.devices = devices
        self._update_ui()

    def _update_ui(self):
        # Clear current labels
        for label in self.device_qlabels:
            self.layout.removeWidget(label)
            label.deleteLater()
        self.device_qlabels.clear()

        for device in self.devices:
            label = QLabel(f"SD card inserted: {device['drive']}")
            self.layout.addWidget(label)
            self.device_qlabels.append(label)

        if not self.devices:
            self.lower_down()
            self.close()
        else:
            self.raise_up()

    def lower_down(self):
        """Set window to initial hidden state without focus."""
        self.hide()

    def raise_up(self):
        """Bring window to front, activate and set focus."""
        self.show()
        self.raise_()
        self.activateWindow()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    devices = [{'drive': 'E:'}, {'drive': 'F:'}, ]
    window = RemovablesView.singleton_instance()
    asyncio.run(window.update_content(devices))
    sys.exit(app.exec_())
