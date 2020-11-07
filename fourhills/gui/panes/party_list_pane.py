from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
import shutil

from fourhills.gui.events import AnchorClickedEvent, ObjectRenamedEvent, ObjectDeletedEvent
from fourhills.gui.utils import get_template_path


class PartyListPane(QtWidgets.QDockWidget):

    path = None

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.party_list = QtWidgets.QListWidget()
        self.party_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setWidget(self.party_list)

        self.create_actions()

        # Allow user options for adding/renaming/deleting parties
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def create_actions(self):
        print("Created actions")
        self.create_party_action = QtWidgets.QAction("&Create Party", self)
        self.rename_party_action = QtWidgets.QAction("&Rename Party", self)
        self.delete_party_action = QtWidgets.QAction("&Delete Party (or parties)", self)

        self.create_party_action.triggered.connect(self.create_party)
        self.rename_party_action.triggered.connect(self.rename_party)
        self.delete_party_action.triggered.connect(self.delete_parties)

    def load(self, path):
        """Search path for YAML files and load them as parties"""
        self.path = path
        self.party_list.clear()

        if not path.is_dir():
            # Path does not exist, ignore
            return

        for party_file in path.rglob("*.yaml"):
            item = QtWidgets.QListWidgetItem(party_file.stem)
            item.setData(Qt.UserRole, party_file.stem)
            self.party_list.addItem(item)

    def show_context_menu(self, point_pos):
        print("Showing context menu")
        if not self.path:
            return

        # Get global position
        global_pos = self.mapToGlobal(point_pos)

        # Create menu and insert actions
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.create_party_action)
        n_selected = len(self.party_list.selectedItems())
        if n_selected == 1:
            menu.addAction(self.rename_party_action)
        if n_selected >= 1:
            menu.addAction(self.delete_party_action)

        # Show context menu at handling position
        menu.exec(global_pos)

    def create_party(self):
        # Get a new name for the party from the user
        party_name, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter new party name",
            "Party name:"
        )

        if not got_name:
            return

        # Check whether an party of that name already exists
        party_path = self.path / (party_name + ".yaml")
        if party_path.is_file():
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot create party {} as it already exists!".format(party_name)
            )
            return

        # Copy the template NPC into the new location
        template_path = get_template_path() / "party.yaml"
        shutil.copy(str(template_path), str(party_path))

        # Load up self again to load new entity
        self.load(self.path)

        # Open the new party
        url = f"party://{party_name}"
        QtCore.QCoreApplication.postEvent(
            QtCore.QCoreApplication.instance(),
            AnchorClickedEvent(QtCore.QUrl(url))
        )

    def rename_party(self):
        party = self.party_list.selectedItems()[0]
        old_party_name = party.data(Qt.UserRole)
        old_party_path = self.path / (old_party_name + ".yaml")

        # Get a new name for the party from the user
        new_party_name, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter new party name",
            "Party name:",
            text=old_party_name,
        )

        if not got_name:
            return

        # Check whether an party of that name already exists
        new_party_path = self.path / (new_party_name + ".yaml")
        if new_party_path.is_file():
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot rename {} to {} as it already exists!".format(
                    old_party_name,
                    new_party_name
                )
            )
            return

        shutil.move(str(old_party_path), str(new_party_path))

        # Reload entities
        self.load(self.path)

        # Emit an event to make sure all relevant open windows reload
        QtCore.QCoreApplication.postEvent(
            QtCore.QCoreApplication.instance(),
            ObjectRenamedEvent("Party", old_party_name, new_party_name)
        )

    def delete_parties(self):
        items = self.party_list.selectedItems()
        paths = []
        for item in items:
            party_name = item.data(Qt.UserRole)
            party_path = self.path / (party_name + ".yaml")

            if not party_path.is_file():
                QtWidgets.QErrorMessage.showMessage(
                    "Cannot delete party {} as source file does not exist!".format(
                        party_name
                    )
                )
                return

            paths += [party_path]

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
        for party_path in paths:
            party_path.unlink()
            QtCore.QCoreApplication.postEvent(
                QtCore.QCoreApplication.instance(),
                ObjectDeletedEvent("Party", party_path.stem)
            )

        # Reload widget after deletion
        self.load(self.path)
