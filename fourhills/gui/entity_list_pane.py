from pathlib import Path
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
import shutil

from fourhills.gui.anchor_clicked_event import AnchorClickedEvent


class EntityListPane(QtWidgets.QDockWidget):

    path = None

    def __init__(self, title, entity_type, parent=None):
        super().__init__(title, parent)
        self.entity_type = entity_type
        self.entity_list = QtWidgets.QListWidget()
        self.setWidget(self.entity_list)

        # Allow user options for adding/deleting entities
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def load(self, path):
        """Search path for YAML files and load them as entities"""
        self.path = path
        self.entity_list.clear()

        if not path.is_dir():
            # Path does not exist, ignore
            return

        for entity_file in path.rglob("*.yaml"):
            item = QtWidgets.QListWidgetItem(entity_file.stem)
            item.setData(Qt.UserRole, (self.entity_type, entity_file.stem))
            self.entity_list.addItem(item)

    def show_context_menu(self, point_pos):
        if not self.path:
            return

        # Get global position
        global_pos = self.mapToGlobal(point_pos)

        # Create menu and insert actions
        menu = QtWidgets.QMenu(self)
        menu.addAction(f"Create {self.entity_type}", self.create_entity)

        # Show context menu at handling position
        menu.exec(global_pos)

    def create_entity(self):
        # Get a new name for the entity from the user
        entity_name, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter new {} name".format(self.entity_type),
            "{} name:".format(self.entity_type)
        )

        if not got_name:
            return

        # Check whether an entity of that name already exists
        entity_path = self.path / (entity_name + ".yaml")
        if entity_path.is_file():
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot create {} {} as it already exists!".format(self.entity_type, entity_name)
            )
            return

        # Copy the template NPC into the new location
        template_path = Path(__file__).parents[1] / "templates" / f"{self.entity_type.lower()}.yaml"
        shutil.copy(str(template_path), str(entity_path))

        # Load up self again to load new entity
        self.load(self.path)

        # Open the new entity
        url = f"{self.entity_type.lower()}://{entity_name}"
        QtCore.QCoreApplication.postEvent(
            QtCore.QCoreApplication.instance(),
            AnchorClickedEvent(QtCore.QUrl(url))
        )
