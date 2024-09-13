import sys
from typing import Any, Optional

from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QSystemTrayIcon, QMenu, QAction, \
    QHBoxLayout, QScrollArea, QApplication, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QWidget

from logger import trace
from my_qtclasses import *
from my_qtutils import *


class ProgramViewQ(QWidget):
    # Signal for exiting the application
    to_exit_application = pyqtSignal()
    qts_user_action = pyqtSignal(object)  # means [Any] as argument to be sent with the signal

    def __init__(self):
        super().__init__()
        self._devices = []

        # Set window title, icon, size
        self.setWindowTitle("CondoCopy3 v.0")
        self.setWindowIcon(QIcon("icon1.png"))
        self.setMinimumSize(500, 220)  # Minimum size set to 500x220

        # Main window layout
        _window_layout = QVBoxLayout()
        _window_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_window_layout)

        # Upper widget setup
        self.upper_widget = QWidget()
        self.upper_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        _window_layout.addWidget(self.upper_widget)
        _upper_layout = QHBoxLayout()
        _upper_layout.setContentsMargins(0, 0, 0, 0)
        self.upper_widget.setLayout(_upper_layout)

        # Upper widget content
        self.status_label = QLabel("... no removables ...(initial)")
        _upper_layout.addWidget(self.status_label)
        # Stretch between label and indicator
        _upper_layout.addStretch(1)
        self.mon_indic = MonitoringIndicatorBulb()  # MonitoringIndicatorBulb
        _upper_layout.addWidget(self.mon_indic)

        # weirdo but:
        # _window_layout -> QScrollArea -> device_container_widget -> device_container_layout
        #
        # V---------                             ---------V

        # Middle widget setup (QScrollArea)
        self.middle_scrollarea = QScrollArea()
        self.middle_scrollarea.setWidgetResizable(True)
        self.middle_scrollarea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        _window_layout.addWidget(self.middle_scrollarea)

        # Middle QScrollArea content
        self.device_container_widget = QWidget()            # ! IMPORTANT
        self.device_container_layout = QVBoxLayout()        # ! IMPORNANT
        self.device_container_layout.setSpacing(1)
        self.device_container_widget.setLayout(self.device_container_layout)
        self.middle_scrollarea.setWidget(self.device_container_widget)

        # Footer widget setup
        self.lower_widget = QWidget()
        self.lower_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        _window_layout.addWidget(self.lower_widget)
        _footer_layout = QHBoxLayout()
        _footer_layout.setContentsMargins(0, 0, 0, 0)
        self.lower_widget.setLayout(_footer_layout)

        # Footer widget content:  buttons
        self.to_tray_button = QPushButton("To Tray")
        _footer_layout.addWidget(self.to_tray_button)
        self.close_button = QPushButton("Close")
        _footer_layout.addWidget(self.close_button)
        # Connect buttons
        self.to_tray_button.clicked.connect(self.minimize_to_tray)
        self.close_button.clicked.connect(self.perform_exit)

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

    def adjust_size_and_position(self):
        # Ensure that the widget size adjusts according to its content
        self.adjustSize()

        # Ensure that the window does not shrink below the minimum size
        new_width = max(self.width(), self.minimumWidth())
        new_height = max(self.height(), self.minimumHeight())

        # Check for maximum window size
        available_size = self.screen().availableGeometry()
        max_width = available_size.width()
        max_height = available_size.height()

        # Limit the window size to the maximum screen size
        new_width = min(new_width, max_width)
        new_height = min(new_height, max_height)

        self.resize(new_width, new_height)

        # Center the window on the screen after resizing
        self.center_window()

    def on_visualize_req(self, devices: Optional[list[dict]]):
        # Local consts
        BUTTON_EDGE = 30

        # Check if just clearing needed
        if devices is None:
            # Renew top_layout status string
            self.status_label.setText("... no removables ... (initial)")
            # Clear layout
            trace("layout to clear")
            while self.device_container_layout.count():
                extracted_layout_item = self.device_container_layout.takeAt(0)
                widget_to_delete = extracted_layout_item.widget()
                if widget_to_delete:
                    # clear widget object
                    widget_to_delete.deleteLater()

            self._devices = devices
            return

        # Explicitly ensure devices are lists
        previous_devices = self._devices or []
        current_devices = devices or []

        # Define removed and added lists
        removed_devices = [d for d in previous_devices if d not in current_devices]
        added_devices = [d for d in current_devices if d not in previous_devices]

        self._devices = devices

        # Check if no changes given
        if removed_devices == added_devices == []:
            return

        # Apply changes
        if not devices:
            self.status_label.setText("No removables.")
        else:
            self.status_label.setText("Removables found.")

        # Vizually remove 'removed'
        # todo

        spacer = QSpacerItem(20, 5, QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Vizually add 'added'
        for device in devices:
            # Create the device holder strip with the layout
            current_device_holder = QWidget()
            current_device_holder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            holder_layout = QHBoxLayout(current_device_holder)
            holder_layout.setContentsMargins(0, 0, 0, 0)

            # Create the device info label the placeholder for buttons
            curr_device_label = QLabel(f"{device['drive']} -- {device['id']} -- {device.get('model', 'None')}")
            button_holder = QWidget()

            # Compose strip
            holder_layout.addWidget(curr_device_label)
            holder_layout.addStretch(1)
            holder_layout.addWidget(button_holder)

            # Add  before  last  QSpacerItem
            add_before_last_spacer(self.device_container_layout, current_device_holder, spacer)

            # Refine buttons management
            button_holder.setMinimumSize(BUTTON_EDGE, BUTTON_EDGE)
            button_holder.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            button_holder_layout = QHBoxLayout(button_holder)
            button_holder_layout.setContentsMargins(0, 0, 0, 0)
            # Create buttons if needed
            if device.get('model') is not None:
                copy_button = QPushButton("C")
                move_button = QPushButton("M")
                see_button = QPushButton("see")

                # Make buttons small and square
                copy_button.setFixedSize(BUTTON_EDGE, BUTTON_EDGE)
                move_button.setFixedSize(BUTTON_EDGE, BUTTON_EDGE)
                see_button.setFixedSize(BUTTON_EDGE, BUTTON_EDGE)

                button_holder_layout.addWidget(copy_button)
                button_holder_layout.addWidget(move_button)
                button_holder_layout.addWidget(see_button)

        # Adjust window size based on content
        self.adjust_size_and_position()

# ---


class MonitoringIndicatorBulb(QWidget):
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



# For testing purposes:
if __name__ == "__main__":
    # Create the application object
    app = QApplication(sys.argv)

    # Create the main window object
    window = ProgramViewQ()

    # Show the window
    window.show()

    # Create a list of devices to simulate data change
    devices = [
        {'drive': 'G:', 'id': 'BULBA1_ABC162', 'model': None},
        {'drive': 'H:', 'id': 'NO_LABEL_MCBOA', 'model': 'DCIF_compatible'}
    ]

    # Set a QTimer to call the on_data_changed method after 5 seconds
    QTimer.singleShot(5000, lambda: window.on_visualize_req(devices))

    # Set a QTimer to call the on_data_changed method after 10 seconds
    # Create a list of devices to simulate data change
    devices2 = [
        {'drive': 'G:', 'id': 'BULBA1_ABC162', 'model': None},
        {'drive': 'H:', 'id': 'NO_LABEL_MCBOA', 'model': 'DCIF_compatible'},
        {'drive': 'I:', 'id': 'USB_1A2B3C4D', 'model': 'SanDisk_32GB'},
        {'drive': 'J:', 'id': 'KINGSTON_XYZ123', 'model': 'Kingston_64GB'},
        {'drive': 'K:', 'id': 'SEAGATE_BACKUP', 'model': 'Seagate_1TB'},
        {'drive': 'L:', 'id': 'WD_BLACK1TB', 'model': 'WD_1TB_Black'},
        {'drive': 'M:', 'id': 'PNY_FLASH_512GB', 'model': 'PNY_512GB'},
        {'drive': 'N:', 'id': 'SAMSUNG_EVO_500GB', 'model': 'Samsung_EVO_500GB'},
        {'drive': 'O:', 'id': 'TOSHIBA_HDD_2TB', 'model': 'Toshiba_2TB'},
        {'drive': 'P:', 'id': 'CRUCIAL_SSD_1TB', 'model': 'Crucial_1TB_SSD'},
        {'drive': 'Q:', 'id': 'HITACHI_HDD_3TB', 'model': 'Hitachi_3TB'},
        {'drive': 'R:', 'id': 'LEXAR_FLASH_128GB', 'model': 'Lexar_128GB'},
        {'drive': 'S:', 'id': 'VERBATIM_STORE_N_GO', 'model': 'Verbatim_64GB'},
        {'drive': 'T:', 'id': 'CORSAIR_FLASH_VOYAGER', 'model': 'Corsair_Voyager_256GB'},
        {'drive': 'U:', 'id': 'PATRIOT_SUPERSONIC_RAGE', 'model': 'Patriot_Rage_128GB'}
    ]
    QTimer.singleShot(10_000, lambda: window.on_visualize_req(devices2))

    # Start the application's event loop
    sys.exit(app.exec_())
