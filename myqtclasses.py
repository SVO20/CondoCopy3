from PyQt5.QtWidgets import QWidget, QLayout
from typing import List, Tuple, Optional, Any

from logger import error, info, warning, debug, trace


class MarkMamager(QLayout):
    """Mixin class for QLayout providing methods to find and remove items based on properties."""

    def findItemsByProperty(self,
                            property_name: str,
                            property_value: Any) -> Tuple[List[QLayout], List[QWidget]]:
        """Finds widgets and layouts within the current layout that have a specific property.

        :param property_name: The property name to search for.
        :param property_value: The property value to match.
        :return: A tuple containing a list of matching QLayouts and a list of matching QWidgets.
        """

        matching_layouts: List[QLayout] = []
        matching_widgets: List[QWidget] = []

        # Start from self check
        if self.property(property_name) == property_value:
            matching_layouts.append(self)

        # Recursive check child elements
        def _cascade_search(layout: QLayout) -> None:
            """Recursively searches for items in the layout that match the given property"""
            for i in range(layout.count()):
                item = layout.itemAt(i)
                widget = item.widget()
                child_layout = item.layout()

                if widget and widget.property(property_name) == property_value:
                    matching_widgets.append(widget)

                if child_layout:
                    if child_layout.property(property_name) == property_value:
                        matching_layouts.append(child_layout)
                    _cascade_search(child_layout)
        _cascade_search(self)

        debug(f"Found {len(matching_widgets)} widgets and {len(matching_layouts)} layouts "
              f"with property '{property_name}={property_value}'")
        return matching_layouts, matching_widgets

    def removeItemsByProperty(self,
                              property_name: str,
                              property_value: Any) -> None:
        """Removes widgets and layouts from the current layout based on a specific property.

        :param property_name: The property name to search for.
        :param property_value: The property value to match.
        :return: None
        """

        def _cascade_remove(items: list) -> None:
            """Recursively removes widgets and layouts, including all their child widgets and layouts."""
            for item in items:
                if isinstance(item, QWidget):
                    # Check if the widget has a parent widget
                    parent_widget = item.parentWidget()
                    if parent_widget:
                        # Check if the parent has a layout
                        parent_layout = parent_widget.layout()
                        if parent_layout:
                            # Remove the widget from the parent's layout
                            parent_layout.removeWidget(item)
                            debug(
                                f"Widget {item.objectName() if item.objectName() else item} removed from parent layout.")
                        else:
                            warning(
                                f"Widget {item.objectName() if item.objectName() else item} has no parent layout.")
                    else:
                        warning(
                            f"Widget {item.objectName() if item.objectName() else item} has no parent widget.")

                    # Delete the widget itself
                    item.deleteLater()
                    debug(f"Widget {item.objectName() if item.objectName() else item} deleted.")

                elif isinstance(item, QLayout):
                    # Recursively remove all child elements in the layout
                    while item.count():
                        child_item = item.takeAt(0)
                        if child_item.widget():
                            # If it's a widget, delete it
                            child_item.widget().deleteLater()
                            debug(
                                f"Child widget {child_item.widget().objectName() if child_item.widget().objectName() else child_item.widget()} deleted.")
                        elif child_item.layout():
                            # If it's a nested layout, recursively remove it
                            _cascade_remove([child_item.layout()])

                    # Remove the layout itself
                    item.setParent(None)  # Disconnect it from its parent
                    debug(f"Layout {item} removed.")

        # Start from self check
        if self.property(property_name) == property_value:
            # Only one deletion operation needed
            _cascade_remove([self])
            debug(f"Removing root layout with property '{property_name}={property_value}'")
            return

        found_layouts, found_widgets = self.findItemsByProperty(property_name, property_value)

        if not found_widgets and not found_layouts:
            warning(f"No items found with property '{property_name}={property_value}'")
            return

        debug(f"Removing {len(found_widgets)} widgets and {len(found_layouts)} "
              f"layouts with property '{property_name}={property_value}'")
        _cascade_remove(found_widgets + found_layouts)
        trace(f"Successfully removed items with property '{property_name}={property_value}'")

    def setPropertyAllDescendants(self,
                                  property_name: str,
                                  property_value: Any,
                                  include_self: bool = False):
        # todo
        pass


    def removePropertyAllDescendants(self,
                                     property_name: str,
                                     property_value: Any,
                                     include_self: bool = False):
        # todo
        pass

class MarkedLayout:
    """Mixin class for QLayout providing methods to find and remove items based on properties."""

    def __init__(self, layout: QLayout, name: str, value: Any) -> None:
        """
        :param layout: The base QLayout to be wrapped
        :param name: The property name to be used for marking
        :param value: The value associated with the property
        """
        if not isinstance(layout, QLayout):
            error(f"Expected QLayout, got {type(layout).__name__}")
            raise TypeError(f"Expected QLayout, got {type(layout).__name__}")

        self._layout = layout
        self._property_name = name
        self._property_value = value
        self.setProperty(self._property_name, self._property_value)

        debug(f"MarkedLayout initialized with property '{name}={value}'")

    def addLayout(self, child_layout: QLayout) -> None:
        """Adds a sub-layout to the current layout and 'marks' it with the specified property

        :param child_layout: The QLayout to add as child
        """
        if not isinstance(child_layout, QLayout):
            error(f"Expected QLayout, got {type(child_layout).__name__}")
            raise TypeError(f"Expected QLayout, got {type(child_layout).__name__}")

        self._cascade_assign_property(child_layout)
        self._layout.addLayout(child_layout)

        debug(f"Sub-layout added with property '{self._property_name}={self._property_value}'")

    def addWidget(self, child_widget: QWidget) -> None:
        """Adds a widget to the current layout and 'marks' it with the specified property

        :param child_widget: The QWidget to add
        """
        if not isinstance(child_widget, QWidget):
            error(f"Expected QWidget, got {type(child_widget).__name__}")
            raise TypeError(f"Expected QWidget, got {type(child_widget).__name__}")

        if child_widget.property(self._property_name) is not None:
            warning(f"Overwriting existing property "
                    f"'{self._property_name}' in widget '{child_widget}'")
        child_widget.setProperty(self._property_name, self._property_value)

        self._layout.addWidget(child_widget)
        debug(f"Widget added with property '{self._property_name}={self._property_value}'")

    def findItemsByProperty(self,
                            property_name: str,
                            property_value: Any) -> Tuple[List[QLayout], List[QWidget]]:
        """Finds widgets and layouts within the current layout that have a specific property.

        :param property_name: The property name to search for.
        :param property_value: The property value to match.

        :return: A tuple containing a list of matching layouts and widgets
        """
        matching_layouts: List[QLayout] = []
        matching_widgets: List[QWidget] = []

        # Start from self check
        if self._layout.property(property_name) == property_value:
            matching_layouts.append(self._layout)

        def cascade_search(layout: QLayout) -> None:
            """Recursively searches for items in the layout that match the given property"""
            for i in range(layout.count()):
                item = layout.itemAt(i)
                widget = item.widget()
                child_layout = item.layout()

                if widget and widget.property(property_name) == property_value:
                    matching_widgets.append(widget)

                if child_layout:
                    if child_layout.property(property_name) == property_value:
                        matching_layouts.append(child_layout)
                    cascade_search(child_layout)

        cascade_search(self._layout)

        debug(f"Found {len(matching_widgets)} widgets and {len(matching_layouts)} layouts "
              f"with property '{property_name}={property_value}'")
        return matching_widgets, matching_layouts

    def removeItemsByProperty(self, property_name: str, property_value: Any) -> None:
        """Removes widgets and layouts from the current layout based on a specific property

        :param property_name: The property name to search for
        :param property_value: The property value to match
        """
        # Start from self check
        if self._layout.property(property_name) == property_value:
            # Only one deletion operation needed
            self._cascade_remove([self])
            return

        found_widgets, found_layouts = self.findItemsByProperty(property_name, property_value)

        if not found_widgets and not found_layouts:
            warning(f"No items found with property '{property_name}={property_value}'")
            return

        trace(f"Removing {len(found_widgets)} widgets and {len(found_layouts)} "
              f"layouts with property '{property_name}={property_value}'")

        self._cascade_remove(found_widgets + found_layouts)
        debug(f"Successfully removed items with property '{property_name}={property_value}'")

    def __getattr__(self, attr: str):
        """Proxy for accessing attributes of the original layout.
            HINT: The attribute resolution follows order:
                search in the instance,
                then in the class and its ancestors,
                including mixins,
                and if not found, __getattr__ is called for dynamic attribute creation.

        :param attr: the attribute name to access

        :return: The attribute value from the original wrapped layout.
        """
        return getattr(self._layout, attr)

    # ---service----------------

    def _cascade_remove(self, items: list) -> None:
        """Recursively removes items"""

        for item in items:
            if isinstance(item, QWidget):
                parent_layout = item.parentWidget().layout() if item.parentWidget() else None
                if parent_layout:
                    parent_layout.removeWidget(item)
                item.deleteLater()
            elif isinstance(item, QLayout):
                while item.count():
                    child_item = item.takeAt(0)
                    if child_item.widget():
                        child_item.widget().deleteLater()
                    elif child_item.layout():
                        self.cascadeRemove([child_item.layout()])
                item.setParent(None)

    def _cascade_assign_property(self, layout: QLayout) -> None:
        """Recursively assign property to all child layouts and widgets within a layout"""
        if layout.property(self._property_name) is not None:
            warning(f"Overwriting existing property "
                    f"'{self._property_name}' in layout '{layout}'")
        layout.setProperty(self._property_name, self._property_value)

        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            child_layout = item.layout()

            if widget:
                if widget.property(self._property_name) is not None:
                    warning(f"Overwriting existing property "
                            f"'{self._property_name}' in widget '{widget}'")
                widget.setProperty(self._property_name, self._property_value)

            if child_layout:
                self._cascade_assign_property(child_layout)


class LayoutComposer:
    """Factory class to create MarkedLayouts with specified properties"""
    # #use example:
    # QVBoxLayoutComposer = LayoutComposer(QVBoxLayout)
    # main_layout = QVBoxLayoutComposer.create_new('main')
    #
    # # Nest elements
    # child_layout_1 = QVBoxLayout()
    # child_layout_2 = QHBoxLayout()

    # widget_1 = QLabel("Widget 1")
    # widget_2 = QLabel("Widget 2")

    # child_layout_1.addWidget(widget_1)
    # child_layout_2.addWidget(widget_2)

    # main_layout.addLayout(child_layout_1)
    # main_layout.addLayout(child_layout_2)
    # # ALL nested layouts and widgets shall has 'mark' property with 'main' value


    def __init__(self,
                 layout_cls: type,
                 value: Optional[Any] = None,
                 name: str = 'mark') -> None:
        """
        :param layout_cls: the descendant class of QLayout to create
        :param value: default property value to 'mark' layouts with
        :param name: default property name to use for 'mark'

        :raises TypeError: if  layout_cls  is not a subclass of QLayout
        """
        if not issubclass(layout_cls, QLayout):
            error(f"layout_cls must be a subclass of QLayout, got {layout_cls.__name__}")
            raise TypeError(f"layout_cls must be a subclass of QLayout, got {layout_cls.__name__}")

        self._layout_cls = layout_cls
        self._customPropertyName: str = name
        self._customPropertyValue: Optional[Any] = value

        info(f"LayoutComposer factory initialized with "
             f"layout_cls={layout_cls.__name__}, name={name}, value={value}")

    def create_new(self, value: Optional[Any] = None, name: Optional[str] = None) -> MarkedLayout:
        """Main method to create a new MarkedLayout instance.
        :param value: The property value
        :param name: The property name
        :return: the instance of MarkedLayout

        :raises ValueError: if no  value  is provided and no default  value  was set during init
        """
        if name is None:
            name = self._customPropertyName
        if value is None:
            if self._customPropertyValue is not None:
                value = self._customPropertyValue
            else:
                error(f"{name} property value must be set "
                      f"(not provided at LayoutComposer init)")
                raise ValueError(f"{name} property value must be set "
                                 f"(not provided at LayoutComposer init)")

        layout = self._layout_cls()
        marked_layout = MarkedLayout(layout, name, value)
        info(f"Created new MarkedLayout with property '{name}={value}'")
        return marked_layout


# # test
#
# if __name__ == "__main__":
#     import sys
#     from PyQt5.QtWidgets import QApplication, QLabel, QHBoxLayout,QVBoxLayout
#
#     app = QApplication(sys.argv)
#
#     # Create main layout and child elements
#     main_layout: QVBoxLayout = LayoutComposer(QVBoxLayout).create_new('test_value', 'test_property')
#
#     child_layout_1 = QVBoxLayout()
#     child_layout_2 = QHBoxLayout()
#
#     widget_1 = QLabel("Widget 1")
#     widget_2 = QLabel("Widget 2")
#     widget_3 = QLabel("Widget 3")
#
#     # Nest elements
#     child_layout_1.addWidget(widget_1)
#     child_layout_2.addWidget(widget_2)
#     child_layout_1.addLayout(child_layout_2)
#     main_layout.addLayout(child_layout_1)
#     main_layout.addWidget(widget_3)
#
#     # Check that the property is recursively assigned to all elements
#     assert main_layout.property('test_property') == 'test_value', "main_layout property not set correctly"
#     assert child_layout_1.property('test_property') == 'test_value', "child_layout_1 property not set correctly"
#     assert child_layout_2.property('test_property') == 'test_value', "child_layout_2 property not set correctly"
#     assert widget_1.property('test_property') == 'test_value', "widget_1 property not set correctly"
#     assert widget_2.property('test_property') == 'test_value', "widget_2 property not set correctly"
#     assert widget_3.property('test_property') == 'test_value', "widget_3 property not set correctly"
#
#     print("All tests passed!")
