from PyQt5 import QtWidgets


class DeselectableTree(QtWidgets.QTreeWidget):
    def mousePressEvent(self, event):
        self.clearSelection()
        super().mousePressEvent(event)
