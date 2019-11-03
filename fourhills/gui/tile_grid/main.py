from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

from fourhills.gui.tile_grid import TileGridWidget


class MainTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("TestTileGridLayout")
        self.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.root_layout_widget = QtWidgets.QWidget(self.centralwidget)
        self.root_layout_widget.setObjectName("root_layout_widget")
        self.root_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.root_layout.setObjectName("root_layout")

        self.tile_grid = TileGridWidget(self.root_layout_widget, 4, 4)

        button1 = QtWidgets.QPushButton("One")
        button2 = QtWidgets.QPushButton("Two")
        button3 = QtWidgets.QPushButton("Three")
        button4 = QtWidgets.QPushButton("Four")
        self.tile_grid.layout.addWidget(button1, 0, 0, 1, 1)
        self.tile_grid.layout.addWidget(button2, 1, 1, 2, 2)
        self.tile_grid.layout.addWidget(button3, 3, 2, 1, 2)
        self.tile_grid.layout.addWidget(button4, 3, 0, 1, 1)

        # Final window setup
        self.root_layout.addWidget(self.tile_grid)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setLayout(self.root_layout)


def main():
    import sys
    app = QApplication([])
    app.setApplicationName("TileGridLayout Demo")
    window = MainTestWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
