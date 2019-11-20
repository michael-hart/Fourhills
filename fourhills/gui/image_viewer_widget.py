from pathlib import Path
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt


class ImageViewerWidget(QtWidgets.QWidget):

    scale_factor = 1.0

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.layout.addWidget(self.scroll_area)

        self.image_label = QtWidgets.QLabel(self.scroll_area)
        self.scroll_area.setWidget(self.image_label)

        self.image_label.setBackgroundRole(QtGui.QPalette.Dark)
        self.image_label.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored,
            QtWidgets.QSizePolicy.Ignored
        )
        self.image_label.setScaledContents(True)

        self.scroll_area.setBackgroundRole(QtGui.QPalette.Dark)
        self.scroll_area.setVisible(True)

        self.create_actions()

    def create_actions(self):
        self.zoom_in_action = QtWidgets.QAction("Zoom In", self)
        self.zoom_out_action = QtWidgets.QAction("Zoom Out", self)

        self.zoom_in_action.setShortcut(QtGui.QKeySequence.ZoomIn)
        self.addAction(self.zoom_in_action)

        self.zoom_out_action.setShortcut(QtGui.QKeySequence.ZoomOut)
        self.addAction(self.zoom_out_action)

        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_out_action.triggered.connect(self.zoom_out)

    def load_file(self, image_path: Path):
        pixmap = QtGui.QPixmap(str(image_path))
        self.image_label.setPixmap(pixmap)
        self.image_label.resize(pixmap.size())

    def zoom_in(self):
        self.scale_image(1.25)

    def zoom_out(self):
        self.scale_image(0.8)

    def scale_image(self, factor):
        self.scale_factor *= factor
        # pix_size = self.image_label.pixmap().size()
        # scaled_size = (self.scale_factor * pix_size[0], self.scale_factor * pix_size[1])
        self.image_label.resize(self.scale_factor * self.image_label.pixmap().size())

        self.adjust_scroll_bar(self.scroll_area.horizontalScrollBar(), factor)
        self.adjust_scroll_bar(self.scroll_area.verticalScrollBar(), factor)

        self.zoom_in_action.setEnabled(self.scale_factor < 3.0)
        self.zoom_out_action.setEnabled(self.scale_factor > 0.333)

    def adjust_scroll_bar(self, scroll_bar, factor):
        half_step = scroll_bar.pageStep() / 2
        adjusted_step = (factor - 1) * half_step
        scroll_value = int(factor * scroll_bar.value() + adjusted_step)
        scroll_bar.setValue(scroll_value)

    def wheelEvent(self, event):
        if QtWidgets.QApplication.keyboardModifiers() & Qt.ControlModifier:
            # TODO scroll
            y_scroll = event.angleDelta().y()
            if y_scroll > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            super().wheelEvent(event)
        # super().wheelEvent(event)
        # x = event.angleDelta()
        # print(f"Got wheel event pixel delta (x,y)=({x.x()},{x.y()}):")
        # ctrl_held = QtWidgets.QApplication.keyboardModifiers() & Qt.ControlModifier
        # print("Control is held:", ctrl_held)
