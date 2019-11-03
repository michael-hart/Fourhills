import os
import glob
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


class EntityListPane(QtWidgets.QDockWidget):

    def __init__(self, title, entity_type, parent=None):
        super().__init__(title, parent)
        self.entity_type = entity_type
        self.entity_list = QtWidgets.QListWidget()
        self.setWidget(self.entity_list)

    def load(self, path):
        """Search path for YAML files and load them as entities"""
        self.entity_list.clear()

        if not os.path.isdir(str(path)):
            # Path does not exist, ignore
            return

        for entity_file in glob.glob(str(path / "*.yaml"), recursive=True):
            rel_path = os.path.relpath(entity_file, path)
            rel_path.replace(os.path.sep, "/")

            item = QtWidgets.QListWidgetItem(rel_path)
            # item.setText(rel_path)
            item.setData(Qt.UserRole, (self.entity_type, entity_file))
            self.entity_list.addItem(item)
