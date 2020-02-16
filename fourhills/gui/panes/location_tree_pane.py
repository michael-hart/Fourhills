from pathlib import Path
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
import shutil

from fourhills.gui.events import AnchorClickedEvent, ObjectDeletedEvent, ObjectRenamedEvent
from fourhills.gui.utils.make_tree import make_tree_from_path
from fourhills.gui.utils import get_template_path


class LocationTreePane(QtWidgets.QDockWidget):

    path = None

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.location_tree = QtWidgets.QTreeWidget(self)
        self.location_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setWidget(self.location_tree)

        # Allow user options for adding/renaming/deleting locations
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def load(self, path):
        """Search path for YAML files and load them as locations"""
        self.path = path
        self.location_tree.clear()

        if not path.is_dir():
            # Path does not exist, ignore
            return

        top_level = make_tree_from_path(
            path,
            "location.yaml",
            include_files=False
        )
        self.location_tree.addTopLevelItems(top_level)

    def show_context_menu(self, point_pos):
        if self.path is None:
            return

        # Get global position
        global_pos = self.mapToGlobal(point_pos)

        # Create menu and insert actions
        menu = QtWidgets.QMenu(self)
        n_selected = len(self.location_tree.selectedItems())
        if n_selected <= 1:
            menu.addAction(f"Create Location", self.create_location)
        if n_selected == 1:
            menu.addAction(f"Rename Location", self.rename_location)
        if n_selected >= 1:
            menu.addAction(f"Delete Location(s)", self.delete_locations)

        # Show context menu at handling position
        menu.exec(global_pos)

    def create_location(self):
        # Get a new name for the location from the user
        loc_name, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter new location name",
            "Location name:"
        )

        if not got_name:
            return

        # Build path to desired location
        base_path = self.path
        selected_locs = self.location_tree.selectedItems()
        if selected_locs:
            item = selected_locs[0]
            directories = [item.text(0)]
            while item.parent() is not None:
                directories += [item.parent().text(0)]
                item = item.parent()

            directories.reverse()
            for directory in directories:
                base_path = base_path / directory

        # Check whether a location of that name already exists in the current folder
        new_path = base_path / loc_name
        if new_path.is_dir():
            # Show error message
            QtWidgets.QErrorMessage.showMessage(
                    "Cannot create location {} as it already exists!".format(
                        new_path
                    )
                )
            return

        # Copy the template location into the new location
        template_path = get_template_path() / "location"
        shutil.copytree(str(template_path), str(new_path))

        # Load up self again to load new location
        self.load(self.path)

        # Post event to main requesting the new location be opened
        rel_path = new_path.relative_to(self.path)
        url = "location://" + str(rel_path).replace("\\", "/")
        QtCore.QCoreApplication.postEvent(
            QtCore.QCoreApplication.instance(),
            AnchorClickedEvent(QtCore.QUrl(url))
        )

    def rename_location(self):
        old_loc = self.location_tree.selectedItems()[0]

        # Get a new name for the location from the user
        new_loc_name, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter new location name",
            "Location name:",
            text=old_loc.text(0)
        )

        if not got_name:
            return

        directories = []
        item = old_loc
        while item.parent() is not None:
            directories += [item.parent().text(0)]
            item = item.parent()

        directories.reverse()
        base_path = self.path / Path(*directories)

        old_loc_path = base_path / old_loc.text(0)
        new_loc_path = base_path / new_loc_name

        # Check whether requested location already exists
        if new_loc_path.is_dir():
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot rename {} to {} as it already exists!".format(
                    old_loc_path,
                    new_loc_path
                )
            )
            return

        shutil.move(old_loc_path, new_loc_path)

        # Reload locations
        self.load(self.path)

        # Post event that location has been renamed
        old_loc_rel_path = old_loc_path.relative_to(self.path)
        new_loc_rel_path = new_loc_path.relative_to(self.path)
        QtCore.QCoreApplication.postEvent(
            QtCore.QCoreApplication.instance(),
            ObjectRenamedEvent("Location", old_loc_rel_path, new_loc_rel_path)
        )

    def delete_locations(self):

        # Get selected items ready for deletion
        items = self.location_tree.selectedItems()
        paths = []
        for item in items:
            directories = [item.text(0)]
            cur_item = item
            while cur_item.parent() is not None:
                directories += [cur_item.parent().text(0)]
                cur_item = cur_item.parent()
            directories.reverse()
            cur_path = self.path / Path(*directories)
            paths += [cur_path]

        # Make sure they all still exist
        for path in paths:
            if not path.is_dir():
                QtWidgets.QErrorMessage.showMessage(
                    "Cannot delete {} as source folder does not exist!".format(
                        path.relative_to(self.path)
                    )
                )
                return

        # Show confirmation dialog before deleting
        path_str = "\n".join(str(x.relative_to(self.path)) for x in paths)
        confirm_question = "Are you sure you want to delete the following locations?\n" + path_str
        confirmed = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            confirm_question
        )
        if confirmed != QtWidgets.QMessageBox.Yes:
            return

        # Delete and post events for each location
        for loc_path in paths:
            shutil.rmtree(loc_path)
            QtCore.QCoreApplication.postEvent(
                QtCore.QCoreApplication.instance(),
                ObjectDeletedEvent("Location", loc_path.relative_to(self.path))
            )

        # Reload widget after deletion
        self.load(self.path)
