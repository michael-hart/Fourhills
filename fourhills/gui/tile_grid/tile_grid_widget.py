from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore

from mouse_location import MouseLocation
from tile_grid_layout import TileGridLayout


class TileGridWidget(QWidget):

    widget_cache = None
    border_cache = None
    cursor_cache = None

    def __init__(self, parent=None, rows=1, cols=1):
        super().__init__(parent)
        self.layout = TileGridLayout(self, rows, cols)

        # Listen for mouse move events so tiles can be changed
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        # Check if left mouse is still down
        # For now, return is border_cache is not MouseLocation.TopBorder as we're only supporting
        # moves for now
        # If left button still down, get mouse position
        # If in a new grid cell to previous, remove the widget from the grid and layout,
        # and reinsert it in its new position
        pass

    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            return

        pos = event.pos()
        for widget in self.layout.widgets:
            loc = widget.get_mouse_location(pos)
            if loc != MouseLocation.Outside:
                if loc == MouseLocation.Centre:
                    return

                # User has clicked inside the border of a widget, so save all details
                self.widget_cache = widget
                self.border_cache = loc
                self.cursor_cache = widget.CURSORS[loc]

                # Set cursor type to type until mouse is release
                self.setCursor(self.cursor_cache)

                # Return early as event has been handled fully
                return

    def mouseReleaseEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            return

        self.widget_cache = None
        self.border_cache = None
        self.cursor_cache = None
        self.setCursor(QtCore.Qt.ArrowCursor)
