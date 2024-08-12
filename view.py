import sys
from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QSize, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSystemTrayIcon, QMenu, \
    QAction, QHBoxLayout, QScrollArea, QApplication, QSizePolicy

from logger import trace


class ProgramViewQ(QWidget):
    # Signal for exiting the application
    qts_exit_application = pyqtSignal()
    qts_user_condocopymove = pyqtSignal()

    def __init__(self):
        super().__init__()
        trace("Dialog window to create")
        self._devices = []

        # Set window title, icon, size
        self.setWindowTitle("CondoCopy3 v.0")
        self.setWindowIcon(QIcon("icon1.png"))
        self.setMinimumSize(500, 220)  # Minimum size set to 500x220

        # Setting up the interface
        self.layout = QVBoxLayout()

        # Add an initial label for when no devices are detected
        self.info_label = QLabel("... no removables ...")
        self.layout.addWidget(self.info_label)

        # Placeholder layout for device information within a scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.device_widget = QWidget()
        self.device_layout = QVBoxLayout(self.device_widget)
        self.scroll_area.setWidget(self.device_widget)
        self.layout.addWidget(self.scroll_area)

        # Control buttons
        self.to_tray_button = QPushButton("toTray")
        self.close_button = QPushButton("Close")
        self.to_tray_button.clicked.connect(self.minimize_to_tray)
        self.close_button.clicked.connect(self.perform_exit)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.to_tray_button)
        control_layout.addWidget(self.close_button)
        self.layout.addLayout(control_layout)

        self.setLayout(self.layout)

        # Configure window flags to make it appear as the main window on the taskbar
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)

        # Initialize system tray with context menu options
        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), parent=self)
        tray_menu = QMenu(self)
        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self.show_window)
        tray_menu.addAction(restore_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.perform_exit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.adjust_size_and_position()

    def center_window(self):
        """Center the window on the screen."""
        frame_geom = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geom.moveCenter(screen_center)
        self.move(frame_geom.topLeft())

    def closeEvent(self, event):
        # Emit a signal to close the application globally
        self.qts_exit_application.emit()
        event.accept()  # Accept the close event

    def changeEvent(self, event):
        # Minimize to tray if window is minimized
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            self.hide()

    def show_window(self):
        # Restore the window from minimized state
        self.showNormal()

    def perform_exit(self):
        # Hide the system tray icon and close the application
        self.tray_icon.hide()
        self.close()  # This will also trigger the closeEvent

    def minimize_to_tray(self):
        self.hide()

    def on_data_changed(self, devices):
        # Update the UI based on the list of devices
        self._devices = devices
        for i in reversed(range(self.device_layout.count())):
            widget_to_remove = self.device_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.deleteLater()

        if not devices:
            self.info_label.setText("... no removables ...")
            self.info_label.show()
        else:
            self.info_label.hide()
            for device in devices:
                device_info_layout = QHBoxLayout()

                device_info = QLabel(
                    f"{device['drive']}: {device['id']} - {device.get('model', 'None')}")
                device_info_layout.addWidget(device_info)

                # Adding additional buttons if model is present
                if device.get('model') is not None:
                    button_layout = QHBoxLayout()
                    button_layout.addStretch(1)  # Push buttons to the right

                    go_button = QPushButton("go")
                    nome_button = QPushButton("no me")
                    see_button = QPushButton("see")

                    # Make buttons small and square
                    go_button.setFixedSize(30, 30)
                    nome_button.setFixedSize(30, 30)
                    see_button.setFixedSize(30, 30)

                    button_layout.addWidget(go_button)
                    button_layout.addWidget(nome_button)
                    button_layout.addWidget(see_button)

                    device_info_layout.addLayout(button_layout)

                self.device_layout.addLayout(device_info_layout)

        # Adjust window size based on content
        self.adjust_size_and_position()

    def adjust_size_and_position(self):
        # Ensure that the widget size adjusts according to its content
        self.device_widget.adjustSize()
        self.adjustSize()

        # Ensure that the window does not shrink below the minimum size
        new_width = max(self.width(), self.minimumWidth())
        new_height = max(self.height(), self.minimumHeight())
        self.resize(new_width, new_height)

        # Center the window on the screen after resizing
        self.center_window()


# # Example usage:
# if __name__ == "__main__":
#     # Create the application object
#     app = QApplication(sys.argv)
#
#     # Create the main window object
#     window = ProgramViewQ()
#
#     # Show the window
#     window.show()
#
#     # Create a list of devices to simulate data change
#     devices = [
#         {'drive': 'G:', 'id': 'BULBA1_ABC162', 'model': None},
#         {'drive': 'H:', 'id': 'NO_LABEL_MCBOA', 'model': 'DCIF_compatible'}
#     ]
#
#     # Set a QTimer to call the on_data_changed method after 5 seconds
#     QTimer.singleShot(5000, lambda: window.on_data_changed(devices))
#
#     # Start the application's event loop
#     sys.exit(app.exec_())
