import enum
from typing import Tuple
from pathlib import Path
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
import shutil

from fourhills.gui.deselectable_tree_widget import DeselectableTree
from fourhills.gui.events import AnchorClickedEvent, NoteDeletedEvent, NoteRenamedEvent
from fourhills.gui.make_tree import make_tree_from_path


class ItemType(enum.Enum):
    Markdown = 0
    Directory = 1
    NoFile = 2
    Other = 3


class NoteTreePane(QtWidgets.QDockWidget):

    path = None

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.note_tree = DeselectableTree(self)
        self.setWidget(self.note_tree)

        self.create_actions()

        # Allow user options for note management
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def create_actions(self):
        self.create_note_action = QtWidgets.QAction("Create &Note", self)
        self.rename_note_action = QtWidgets.QAction("&Rename Note", self)
        self.delete_note_action = QtWidgets.QAction("&Delete Note", self)
        self.create_folder_action = QtWidgets.QAction("Create &Folder", self)
        self.rename_folder_action = QtWidgets.QAction("&Rename Folder", self)
        self.delete_folder_action = QtWidgets.QAction("&Delete Folder", self)

        self.create_note_action.triggered.connect(self.create_note)
        self.rename_note_action.triggered.connect(self.rename_item)
        self.delete_note_action.triggered.connect(self.delete_item)
        self.create_folder_action.triggered.connect(self.create_folder)
        self.rename_folder_action.triggered.connect(self.rename_item)
        self.delete_folder_action.triggered.connect(self.delete_item)

    def load(self, path):
        """Search path for markdown files and load them as notes"""
        self.path = path
        self.note_tree.clear()

        if not path.is_dir():
            # Path does not exist, ignore
            return

        top_level = make_tree_from_path(path, "*", include_file_endings=True)
        self.note_tree.addTopLevelItems(top_level)

    # TODO context menu
    def show_context_menu(self, point_pos):
        if not self.path:
            return

        # Get global position
        global_pos = self.mapToGlobal(point_pos)

        menu = QtWidgets.QMenu(self)

        _, _type = self.get_selected_item_path()

        if _type == ItemType.Other:
            # Non-markdown files not supported
            return
        elif _type == ItemType.NoFile:
            # Right click in blank space, create file or folder
            menu.addAction(self.create_note_action)
            menu.addAction(self.create_folder_action)
        elif _type == ItemType.Directory:
            # Right click on folder, create/rename/delete folder or create file
            menu.addAction(self.create_note_action)
            menu.addAction(self.create_folder_action)
            menu.addAction(self.rename_folder_action)
            menu.addAction(self.delete_folder_action)
        else:
            # Right click on markdown, create/rename/delete file
            menu.addAction(self.create_note_action)
            menu.addAction(self.rename_note_action)
            menu.addAction(self.delete_note_action)

        # Show context menu at handling position
        menu.exec(global_pos)

    def get_selected_item_path(self) -> Tuple[Path, ItemType]:

        selected = self.note_tree.selectedItems()
        if not selected:
            return (self.path, ItemType.NoFile)

        item = selected[0]

        # Get path of item in question
        path = self.path
        directories = [item.text(0)]
        while item.parent() is not None:
            directories += [item.parent().text(0)]
            item = item.parent()
        directories.reverse()
        for directory in directories:
            path = path / directory

        if path.is_dir():
            return (path, ItemType.Directory)

        if path.name.endswith(".md"):
            return (path, ItemType.Markdown)

        return (path, ItemType.Other)

    def create_note(self):
        folder_path, _ = self.get_selected_item_path()

        new_note_name, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter new note name",
            "Note name:"
        )
        if not got_name:
            return

        # Check whether that path already exists
        new_note_path = folder_path / new_note_name
        if not new_note_name.endswith(".md"):
            new_note_path = Path(str(new_note_path) + ".md")
        if new_note_path.exists():
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot create note {} as it already exists!".format(new_note_path)
            )
            return

        # Copy the template note into the new location
        template_path = Path(__file__).parents[1] / "templates" / "gm_note.md"
        shutil.copy(template_path, new_note_path)

        # Add the new note to the tree and set selected
        tree_widget = QtWidgets.QTreeWidgetItem()
        tree_widget.setText(0, new_note_path.name)

        if self.note_tree.selectedItems():
            selected_item = self.note_tree.selectedItems()[0]
            selected_item.addChild(tree_widget)
            selected_item.setExpanded(True)
        else:
            self.note_tree.addTopLevelItem(tree_widget)
        tree_widget.setSelected(True)

        # Open the new entity
        rel_path_url = '/'.join(new_note_path.relative_to(self.path).parts)
        url = f"note://{rel_path_url}"
        QtCore.QCoreApplication.postEvent(
            QtCore.QCoreApplication.instance(),
            AnchorClickedEvent(QtCore.QUrl(url))
        )

    def create_folder(self):
        folder_path, _ = self.get_selected_item_path()

        new_folder_name, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter new folder name",
            "Folder name:"
        )
        if not got_name:
            return

        # Check whether that path already exists
        new_folder_path = folder_path / new_folder_name
        if new_folder_path.exists():
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot create folder {} as it already exists!".format(new_folder_path)
            )
            return

        # Create the folder
        new_folder_path.mkdir()

        # Add the new folder to the tree and set selected
        tree_widget = QtWidgets.QTreeWidgetItem()
        tree_widget.setText(0, new_folder_path.name)

        if self.note_tree.selectedItems():
            selected_item = self.note_tree.selectedItems()[0]
            selected_item.addChild(tree_widget)
            selected_item.setExpanded(True)
        else:
            self.note_tree.addTopLevelItem(tree_widget)
        tree_widget.setSelected(True)

    def rename_item(self):
        # Get new folder/note name
        old_note_path, _type = self.get_selected_item_path()
        type_string = "note" if _type == ItemType.Markdown else "folder"
        new_note_name, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter new {} name".format(type_string),
            "{} name:".format(type_string.capitalize()),
            text=old_note_path.name
        )

        if not got_name:
            return

        # Check whether a note/folder of that name already exists
        new_note_path = old_note_path.parent / new_note_name
        if new_note_path.exists():
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot rename {} to {} as it already exists!".format(
                    old_note_path.name,
                    new_note_name
                )
            )
            return

        shutil.move(old_note_path, new_note_path)

        # Delete old QTreeWidgetItem and add new item with new name
        new_item = QtWidgets.QTreeWidgetItem()
        new_item.setText(0, new_note_path.name)
        selected_item = self.note_tree.selectedItems()[0]
        if selected_item.parent():
            parent_item = selected_item.parent()
            parent_item.removeChild(selected_item)
            parent_item.addChild(new_item)
        else:
            self.note_tree.removeItemWidget(selected_item, 0)
            self.note_tree.addTopLevelItem(new_item)

        # Emit an event to make sure all relevant open windows reload
        if _type == ItemType.Markdown:
            QtCore.QCoreApplication.postEvent(
                QtCore.QCoreApplication.instance(),
                NoteRenamedEvent(
                    old_note_path.relative_to(self.path),
                    new_note_path.relative_to(self.path)
                )
            )

    def delete_item(self):
        note_path, _type = self.get_selected_item_path()

        type_string = "note" if _type == ItemType.Markdown else "folder"

        confirmed = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this {}?\n{}".format(
                type_string,
                note_path
            )
        )
        if confirmed != QtWidgets.QMessageBox.Yes:
            return

        if _type == ItemType.Directory:
            shutil.rmtree(note_path)
        else:
            note_path.unlink()
            QtCore.QCoreApplication.postEvent(
                QtCore.QCoreApplication.instance(),
                NoteDeletedEvent(note_path.relative_to(self.path))
            )

        # Remove deleted item from tree
        selected_item = self.note_tree.selectedItems()[0]
        if selected_item.parent():
            selected_item.parent().removeChild(selected_item)
        else:
            self.note_tree.removeItemWidget(selected_item, 0)

        # Reload entities after changes
        self.load(self.path)

    # Override mouse handler to allow user to deselect by clicking in blank space
    def mousePressEvent(self, event):
        self.clearSelection()
        super().mousePressEvent(self, event)
