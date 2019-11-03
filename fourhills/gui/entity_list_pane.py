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

        if not path.is_dir():
            # Path does not exist, ignore
            return

        for entity_file in path.rglob("*.yaml"):
            item = QtWidgets.QListWidgetItem(entity_file.stem)
            item.setData(Qt.UserRole, (self.entity_type, str(entity_file)))
            self.entity_list.addItem(item)
