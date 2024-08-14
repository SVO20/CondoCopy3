from typing import Any

from PyQt5.QtCore import QEvent
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QSystemTrayIcon, QMenu, QAction, \
    QHBoxLayout, QScrollArea
from PyQt5.QtWidgets import QWidget

from logger import trace


class MonitoringIndicator(QWidget):
    qts_user_force_monstate = pyqtSignal(bool)  # Signal to force onstate

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)   # Set a fixed size for the indicator
        self._onstate = True        # Initial state is ON
        self._pressed = False       # Track whether the button is being pressed
        self._hover = False         # Track whether the mouse is hovering over the button

    def enterEvent(self, event):
        self._hover = True
        self.update()  # Trigger a repaint
        event.accept()

    def leaveEvent(self, event):
        self._hover = False
        self.update()  # Trigger a repaint
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(0, 255, 0) \
            if self._onstate \
            else QColor(105, 105, 105)  # Green for ON, Dark Gray for OFF
        border_color = QColor(0, 0, 255) \
            if self._hover \
            else QColor(255, 255, 255)  # Border color changes with hover state
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(border_color, 1))
        painter.drawEllipse(2, 2, self.width() - 4, self.height() - 4)

        if self._pressed:
            painter.setBrush(QBrush(color.darker(150)))  # Darker inner circle when pressed
            painter.setPen(QPen(QColor(color.darker(150)), 1))
            painter.drawEllipse(4, 4, self.width() - 8, self.height() - 8)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self.update()  # Update the visual appearance
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = False
            self.update()  # Update the visual appearance
            if self.rect().contains(event.pos()):
                self._onstate = not self._onstate

                # Emit the signal to force new _onstate
                self.qts_user_force_monstate.emit(self._onstate)
        super().mouseReleaseEvent(event)

    def change_onstate(self, onstate: bool):
        """ Change the onstate without emitting a signal. """
        self._onstate = onstate
        self.update()  # Update the visual appearance


class ProgramViewQ(QWidget):
    # Signal for exiting the application
    to_exit_application = pyqtSignal()
    qts_user_action = pyqtSignal(Any)

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

        # Top layout with label and monitoring indicator
        self.top_layout = QHBoxLayout()
        self.status_label = QLabel("... no removables ...")
        self.mon_indic = MonitoringIndicator()
        # Adding the label and monitoring indicator to the top layout
        self.top_layout.addWidget(self.status_label)
        self.top_layout.addStretch(1)  # Push monitoring indicator to the right
        self.top_layout.addWidget(self.mon_indic)
        self.layout.addLayout(self.top_layout)

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
        self.tray_icon = QSystemTrayIcon(QIcon("icon1.png"), parent=self)
        tray_menu = QMenu(self)
        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self.show_window)
        tray_menu.addAction(restore_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.perform_exit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.show_window()
        self.adjust_size_and_position()

    def center_window(self):
        """Center the window on the screen."""
        frame_geom = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geom.moveCenter(screen_center)
        self.move(frame_geom.topLeft())

    def closeEvent(self, event):
        # Emit a signal to close the application globally
        self.to_exit_application.emit()
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

    def on_visualize_req(self, devices):
        # Update the UI based on the list of devices
        self._devices = devices
        for i in reversed(range(self.device_layout.count())):
            widget_to_remove = self.device_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.deleteLater()

        if not devices:
            self.status_label.setText("... no removables ...")
            # Hide the monitoring indicator if no devices are found
            self.status_label.show()
        else:
            self.status_label.setText("Removables Found:")
            # Show the monitoring indicator if devices are found
            for device in devices:
                device_info_layout = QHBoxLayout()

                device_info = QLabel(
                    f"{device['drive']} -- {device['id']} -- {device.get('model', 'None')}")
                device_info_layout.addWidget(device_info)

                # Adding additional buttons if model is present
                # todo vv--  --vv
                if device.get('model') is not None:
                    button_layout = QHBoxLayout()
                    button_layout.addStretch(1)  # Push buttons to the right

                    copy_button = QPushButton("C")
                    move_button = QPushButton("M")
                    see_button = QPushButton("see")

                    # Make buttons small and square
                    copy_button.setFixedSize(30, 30)
                    move_button.setFixedSize(30, 30)
                    see_button.setFixedSize(30, 30)

                    button_layout.addWidget(copy_button)
                    button_layout.addWidget(move_button)
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

# # For testing purposes:
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
