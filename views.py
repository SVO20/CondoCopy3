from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


class SDCardDialog(QDialog):
    def __init__(self, drive, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SD Card Inserted")
        self.drive = drive
        self.init_ui()
        self.start_card_monitoring()

    def init_ui(self):
        layout = QVBoxLayout()
        self.message = QLabel(f"SD card inserted: {self.drive}")
        layout.addWidget(self.message)

        button_ok = QPushButton("OK")
        button_ok.clicked.connect(self.accept)
        layout.addWidget(button_ok)

        self.setLayout(layout)
