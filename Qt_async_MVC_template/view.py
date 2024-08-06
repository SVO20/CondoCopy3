import builtins
import time

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QMutexLocker, QTimer
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QApplication

from logger import debug


class TempView(QWidget):
    button_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    resume_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.label = QLabel("No data")
        self.update_button = QPushButton("Some Button")
        self.pause_button = QPushButton("Pause")
        self.resume_button = QPushButton("Resume")

        self.update_button.clicked.connect(self.button_clicked.emit)
        self.pause_button.clicked.connect(self.pause_clicked.emit)
        self.resume_button.clicked.connect(self.resume_clicked.emit)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.update_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.resume_button)
        self.setLayout(layout)

    @pyqtSlot(str)
    def update_label(self, text):
        self.label.setText(text)
        debug(f"label to update by text: '{text}'")
        self.update()
