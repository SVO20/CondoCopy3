from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox, QApplication
import sys

from logger import trace


class SDCardDialog(QDialog):
    """Info window"""

    _initialized = False
    _instance = None        # <-- SINGLETON instance to be placed here

    @classmethod
    def singleton_instance(cls, devices, parent=None):
        if cls._instance is None:
            cls._instance = SDCardDialog(devices, parent)
        else:
            cls._instance.update_ui(devices)
            cls._instance.show()
            cls._instance.raise_()
            cls._instance.activateWindow()
        return cls._instance

    def __new__(cls, devices, parent=None):
        return super(SDCardDialog, cls).__new__(cls)

    def __init__(self, devices, parent=None):
        if self._initialized:
            # Window already exists
            trace(f"Dialog window to bring up")
            self.devices = devices
            self.update_ui()
            self.show()
            self.raise_()
            self.activateWindow()
            return

        # Window not exists
        trace(f"Dialog window to create")
        super().__init__(parent)
        self.setWindowTitle("Removable inserted")
        self.devices = devices
        self._initialized = True
        self.init_ui()
        self.show()
        self.raise_()
        self.activateWindow()

    def init_ui(self):
        # <=== Window not exists
        self.compose_view()

    def update_ui(self):
        # <=== Window already exists

        # Clear current labels
        for label in self.device_qlabels:
            self.layout.removeWidget(label)
            label.deleteLater()
        self.device_qlabels.clear()

        # Draw new UI with current devices
        self.compose_view()

        # Close the dialog if no devices are connected
        if not self.devices:
            self.close()

    def compose_view(self):
        self.layout = QVBoxLayout()
        self.device_qlabels = []

        # Display each device in a QLabel and add it to the layout
        for device in self.devices:
            label = QLabel(f"SD card inserted: {device}")
            self.layout.addWidget(label)
            self.device_qlabels.append(label)

        self.message = QLabel()
        self.layout.addWidget(self.message)

        button_ok = QPushButton("OK")
        button_ok.clicked.connect(self.accept)
        self.layout.addWidget(button_ok)

        self.setLayout(self.layout)


