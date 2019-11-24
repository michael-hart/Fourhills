from pathlib import Path
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
import shutil

from fourhills.exceptions import FourhillsMonsterImportError
from fourhills.gui.events import AnchorClickedEvent, EntityRenamedEvent, EntityDeletedEvent
from fourhills.utils.import_monster import import_monster
from fourhills.utils.text_utils import slugify


class EntityListPane(QtWidgets.QDockWidget):

    path = None

    def __init__(self, title, entity_type, parent=None):
        super().__init__(title, parent)
        self.entity_type = entity_type

        self.centralwidget = QtWidgets.QWidget()
        self.setWidget(self.centralwidget)
        layout = QtWidgets.QVBoxLayout()
        self.centralwidget.setLayout(layout)

        self.entity_list = QtWidgets.QListWidget()
        self.entity_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.entity_list)

        if entity_type == "Monster":
            # Add Import Monster button
            self.import_btn = QtWidgets.QPushButton("Import Monster", self.centralwidget)
            self.import_btn.pressed.connect(self.on_import_monster)
            layout.addWidget(self.import_btn)

        # Allow user options for adding/renaming/deleting entities
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
        n_selected = len(self.entity_list.selectedItems())
        if n_selected == 1:
            menu.addAction(f"Rename {self.entity_type}", self.rename_entity)
        if n_selected >= 1:
            menu.addAction(f"Delete {self.entity_type}(s)", self.delete_entities)

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
        template_path = Path(__file__).parents[2] / "templates" / f"{self.entity_type.lower()}.yaml"
        shutil.copy(str(template_path), str(entity_path))

        # Load up self again to load new entity
        self.load(self.path)

        # Open the new entity
        url = f"{self.entity_type.lower()}://{entity_name}"
        QtCore.QCoreApplication.postEvent(
            QtCore.QCoreApplication.instance(),
            AnchorClickedEvent(QtCore.QUrl(url))
        )

    def rename_entity(self):
        entity = self.entity_list.selectedItems()[0]
        _, old_entity_name = entity.data(Qt.UserRole)
        old_entity_path = self.path / (old_entity_name + ".yaml")

        # Get a new name for the entity from the user
        new_entity_name, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter new {} name".format(self.entity_type),
            "{} name:".format(self.entity_type),
            text=old_entity_name,
        )

        if not got_name:
            return

        # Check whether an entity of that name already exists
        new_entity_path = self.path / (new_entity_name + ".yaml")
        if new_entity_path.is_file():
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot rename {} to {} as it already exists!".format(
                    old_entity_name,
                    new_entity_name
                )
            )
            return

        shutil.move(str(old_entity_path), str(new_entity_path))

        # Reload entities
        self.load(self.path)

        # Emit an event to make sure all relevant open windows reload
        QtCore.QCoreApplication.postEvent(
            QtCore.QCoreApplication.instance(),
            EntityRenamedEvent(self.entity_type, old_entity_name, new_entity_name)
        )

    def delete_entities(self):

        items = self.entity_list.selectedItems()
        paths = []
        for item in items:
            _, entity_name = item.data(Qt.UserRole)
            entity_path = self.path / (entity_name + ".yaml")

            if not entity_path.is_file():
                QtWidgets.QErrorMessage.showMessage(
                    "Cannot delete {} {} as source file does not exist!".format(
                        self.entity_type, entity_name
                    )
                )
                return

            paths += [entity_path]

        # Show confirmation dialog before deleting
        path_str = "\n".join(str(x) for x in paths)
        confirm_question = "Are you sure you want to delete the following files?\n" + path_str
        confirmed = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            confirm_question
        )
        if confirmed != QtWidgets.QMessageBox.Yes:
            return

        # Delete and post events for each file
        for entity_path in paths:
            entity_path.unlink()
            QtCore.QCoreApplication.postEvent(
                QtCore.QCoreApplication.instance(),
                EntityDeletedEvent(self.entity_type, entity_path.stem)
            )

        # Reload widget after deletion
        self.load(self.path)

    def on_import_monster(self):
        # Present user with dialog box of monster name to import
        monster_name, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter monster name",
            "Monster name (exact):"
        )

        # Check if monster already exists in workspace
        monster_slug = slugify(monster_name)
        monster_underscore_slug = monster_slug.replace("-", "_")
        out_path = self.path / (monster_underscore_slug + ".yaml")
        if out_path.exists():
            QtWidgets.QErrorMessage(self).showMessage(
                f"Cannot create requested monster {monster_slug} as it already exists! "
                "Delete or rename the existing monster and try again."
            )
            return

        try:
            import_monster(monster_slug, out_path)
        except FourhillsMonsterImportError as e:
            msg = "Error during import of monster: {}".format(
                "\n".join(e.args)
            )
            msg += " Try checking DnD Beyond for the monster name to see if it is accessible."
            QtWidgets.QErrorMessage(self).showMessage(msg)
            return

        # Reload monsters
        self.load(self.path)

        # Inform user of success
        QtWidgets.QMessageBox.information(
            self,
            "Monster Import Success",
            f"Successfully imported monster {monster_slug}!"
        )
