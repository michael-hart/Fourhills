from PyQt5.QtWidgets import QWidget
# from PyQt5 import QtCore

from tile_grid_layout import TileGridLayout


class TileGridWidget(QWidget):

    def __init__(self, parent=None, rows=1, cols=1):
        super().__init__(parent)
        self.layout = TileGridLayout(self, rows, cols)
