from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from tile_grid_tile import TileGridTile


class TileGridLayout(QtWidgets.QGridLayout):

    widgets = []

    def __init__(self, parent=None, rows=1, cols=1):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.rows = rows
        self.cols = cols
        self.fill_diagonal()

        # Make sure cell items fill their cells
        self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

    def fill_diagonal(self):
        # Put generic widgets in diagonals, or if row is bigger than cols
        # or vice versa, fill the end row/column
        for idx in range(max(self.rows, self.cols)):
            row = min(idx, self.rows)
            col = min(idx, self.cols)
            item = self.itemAtPosition(row, col)
            if item is None:
                super().addWidget(QtWidgets.QWidget(), row, col)

    # def fill_bottom_right(self):
    #     self.bottom_right_cell = QtWidgets.QWidget()
    #     super().addWidget(self.bottom_right_cell, self.rows - 1, self.cols - 1)

    def set_grid_size(self, rows, cols):
        self.removeWidget(self.bottom_right_cell)
        self.rows = rows
        self.cols = cols
        self.fill_diagonal()

    def addWidget(
            self,
            widget,
            fromRow=0,
            fromCol=0,
            rowSpan=1,
            colSpan=1,
            alignment=Qt.Alignment(0)):

        # TODO check to see if object fits
        widget_wrapper = TileGridTile(
            widget.parentWidget(),
            fromRow,
            fromCol,
            rowSpan,
            colSpan
        )
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget_wrapper.setLayout(layout)
        self.widgets += [widget_wrapper]
        super().addWidget(widget_wrapper, fromRow, fromCol, rowSpan, colSpan, alignment)

    def removeWidget(self, widget):
        # Check list for a TileGridWidget that contains the widget
        correct_wrapper = None
        correct_widget = None
        for wrapper in self.widgets:
            # First position is always layout
            child = wrapper.children()[1]
            if child == widget:
                correct_wrapper = wrapper
                correct_widget = child
                break
        # If the widget was found, remove it
        if correct_wrapper is not None:
            super().removeWidget(correct_widget)
            self.widgets.remove(correct_wrapper)
            correct_widget.hide()
            self.fill_diagonal()
