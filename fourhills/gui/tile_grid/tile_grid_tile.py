import enum
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFrame


class MouseLocation(enum.Enum):
    Centre = 0
    TopBorder = 1
    TopRightBorder = 2
    RightBorder = 3
    BottomRightBorder = 4
    BottomBorder = 5
    BottomLeftBorder = 6
    LeftBorder = 7
    TopLeftBorder = 8


class TileGridTile(QFrame):

    CURSORS = {
        MouseLocation.Centre: QtCore.Qt.ArrowCursor,
        MouseLocation.TopBorder: QtCore.Qt.SizeAllCursor,
        MouseLocation.TopRightBorder: QtCore.Qt.SizeBDiagCursor,
        MouseLocation.RightBorder: QtCore.Qt.SizeHorCursor,
        MouseLocation.BottomRightBorder: QtCore.Qt.SizeFDiagCursor,
        MouseLocation.BottomBorder: QtCore.Qt.SizeVerCursor,
        MouseLocation.BottomLeftBorder: QtCore.Qt.SizeBDiagCursor,
        MouseLocation.LeftBorder: QtCore.Qt.SizeHorCursor,
        MouseLocation.TopLeftBorder: QtCore.Qt.SizeFDiagCursor,
    }
    CORNER_FRACTION = 0.05

    def __init__(self, parent=None, row=0, col=0, rowSpan=1, colSpan=1):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.row_span = rowSpan
        self.col_span = colSpan

        # Box Raised 3 2
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(3)
        self.setMidLineWidth(2)

        # Listen for mouse move events so cursor can be changed
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        # Check if event is just a move or not
        if event.type() == QtCore.QEvent.MouseMove:
            if event.buttons() == QtCore.Qt.NoButton:
                # If mouse is just moving, not dragging, set cursor
                pos = event.pos()
                location = self.get_mouse_location(pos)
                cursor = self.CURSORS[location]
                self.setCursor(cursor)

    def get_mouse_location(self, pos):
        # Get rectangle defining area inside border
        r = self.frameRect()
        w = self.frameWidth()
        r.setX(r.x() + w)
        r.setWidth(r.width() - w)  # Should be 2*w, I don't get why it's not
        r.setY(r.y() + w)
        r.setHeight(r.height() - w)  # and again

        if r.contains(pos):
            return MouseLocation.Centre

        width_low = r.x() + r.width() * self.CORNER_FRACTION
        width_high = r.x() + r.width() - r.width() * self.CORNER_FRACTION
        height_low = r.y() + r.height() * self.CORNER_FRACTION
        height_high = r.y() + r.height() - r.height() * self.CORNER_FRACTION

        right = pos.x() > width_high
        left = pos.x() < width_low
        bottom = pos.y() > height_high
        top = pos.y() < height_low

        if top:
            if right:
                return MouseLocation.TopRightBorder
            elif left:
                return MouseLocation.TopLeftBorder
            else:
                return MouseLocation.TopBorder
        elif bottom:
            if right:
                return MouseLocation.BottomRightBorder
            elif left:
                return MouseLocation.BottomLeftBorder
            else:
                return MouseLocation.BottomBorder
        elif left:
            return MouseLocation.LeftBorder
        else:
            return MouseLocation.RightBorder
