from PyQt5.QtWidgets import QWidget, QLayout, QSpacerItem


def add_before_last_spacer(layout: QLayout, item_to_insert: QWidget, spacer: QSpacerItem) -> None:
    """Inserts an item into the layout just before the last spacer item.
    If no spacer item is found at the end, this function adds one and then inserts the item before it.

    Args:
    layout (QLayout): The layout to modify.
    item_to_insert (QWidget): The widget to be inserted into the layout.
    spacer (QSpacerItem): The spacer item to ensure is at the end of the layout.
    """
    count = layout.count()
    spacer_found = False

    # Check if there are items in the layout
    if count > 0:
        # Get the last item
        last_item = layout.itemAt(count - 1)
        # Check if the last item is a spacer
        if last_item.spacerItem() is not None:
            spacer_found = True

    if not spacer_found:
        # Add spacer at the end of the layout
        layout.addItem(spacer)
        count += 1  # Increase the item count since we've added a spacer

    # Insert the widget or layout second last
    index_to_insert = count - 1  # Position to insert the item
    if isinstance(item_to_insert, QWidget):
        layout.insertWidget(index_to_insert, item_to_insert)
    elif isinstance(item_to_insert, QLayout):
        layout.insertLayout(index_to_insert, item_to_insert)
    else:
        raise TypeError("item_to_insert must be an instance of QWidget or QLayout")


# from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QApplication, QSizePolicy
# import sys
#
# def run_demo():
#     """Creates a simple demo window to visualize the add_before_last_spacer function."""
#     app = QApplication(sys.argv)
#
#     # Creating a main widget and layout
#     main_widget = QWidget()
#     main_widget.setWindowTitle('Demo for add_before_last_spacer')
#     layout = QVBoxLayout(main_widget)
#
#     # Widgets to insert
#     button1 = QPushButton("Button 1")
#     button2 = QPushButton("Button 2")
#     button3 = QPushButton("Button 3")
#     button4 = QPushButton("Add new button")
#
#     # Spacer to be ensured at the end
#     spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
#
#     # Initial setup with some widgets
#     layout.addWidget(button1)
#     layout.addWidget(button2)
#
#     # Ensure the spacer is at the end
#     layout.addSpacerItem(spacer)
#
#     # Use the function to add button3 before the last spacer (or add spacer if not present)
#     add_before_last_spacer(layout, button3, spacer)
#
#     # Dynamic button insertion on click
#     def add_new_button():
#         new_button = QPushButton(f"New Button")
#         add_before_last_spacer(layout, new_button, spacer)
#
#     button4.clicked.connect(add_new_button)
#     layout.addWidget(button4)
#
#     # Show the widget
#     main_widget.show()
#
#     # Start the application loop
#     sys.exit(app.exec_())
#
#
# if __name__ == '__main__':
#     run_demo()
