from pathlib import Path
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
import shutil

from fourhills.gui.events import AnchorClickedEvent, ObjectRenamedEvent, ObjectDeletedEvent


class QuestListPane(QtWidgets.QDockWidget):

    path = None

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.quest_list = QtWidgets.QListWidget()
        self.quest_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setWidget(self.quest_list)

        self.create_actions()

        # Allow user options for adding/renaming/deleting quests
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def create_actions(self):
        self.create_quest_action = QtWidgets.QAction("&Create Quest", self)
        self.rename_quest_action = QtWidgets.QAction("&Rename Quest", self)
        self.delete_quest_action = QtWidgets.QAction("&Delete Quest", self)

        self.create_quest_action.triggered.connect(self.create_quest)
        self.rename_quest_action.triggered.connect(self.rename_quest)
        self.delete_quest_action.triggered.connect(self.delete_quest)

    def load(self, path):
        """Search path for YAML files and load them as quests"""
        self.path = path
        self.quest_list.clear()

        if not path.is_dir():
            # Path does not exist, ignore
            return

        for quest_file in path.rglob("quest.yaml"):
            name = quest_file.parent.name
            item = QtWidgets.QListWidgetItem(name)
            item.setData(Qt.UserRole, name)
            self.quest_list.addItem(item)

    def show_context_menu(self, point_pos):
        if not self.path:
            return

        # Get global position
        global_pos = self.mapToGlobal(point_pos)

        # Create menu and insert actions
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.create_quest_action)
        n_selected = len(self.quest_list.selectedItems())
        if n_selected == 1:
            menu.addAction(self.rename_quest_action)
        if n_selected >= 1:
            menu.addAction(self.delete_quest_action)

        # Show context menu at handling position
        menu.exec(global_pos)

    def create_quest(self):
        # Get a new name for the quest from the user
        quest, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter new quest name",
            "Quest name:",
        )

        if not got_name:
            return

        # Check whether a quest of that name already exists
        quest_path = self.path / quest / "quest.yaml"
        if quest_path.is_file():
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot create quest {} as it already exists!".format(quest_path)
            )
            return

        # Copy the template quest into the new location
        template_path = Path(__file__).parents[2] / "templates" / "quest"
        shutil.copytree(template_path, quest_path.parent)

        # Load up self again for new quest
        self.load(self.path)

        # Open the new quest
        url = f"quest://{quest}"
        QtCore.QCoreApplication.postEvent(
            QtCore.QCoreApplication.instance(),
            AnchorClickedEvent(QtCore.QUrl(url))
        )

    def rename_quest(self):
        quest = self.quest_list.selectedItems()[0]
        old_quest_name = quest.data(Qt.UserRole)
        old_quest_path = self.path / old_quest_name / "quest.yaml"

        # Get a new name for the quest from the user
        new_quest_name, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter new quest name",
            "Quest name:",
            text=old_quest_name,
        )

        if not got_name:
            return

        # Check whether an quest of that name already exists
        new_quest_path = self.path / new_quest_name / "quest.yaml"
        if new_quest_path.is_file():
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot rename {} to {} as it already exists!".format(
                    old_quest_name,
                    new_quest_name
                )
            )
            return

        shutil.move(old_quest_path.parent, new_quest_path.parent)

        # Reload entities
        self.load(self.path)

        # Emit an event to make sure all relevant open windows reload
        QtCore.QCoreApplication.postEvent(
            QtCore.QCoreApplication.instance(),
            ObjectRenamedEvent("Quest", old_quest_name, new_quest_name)
        )

    def delete_quest(self):
        items = self.quest_list.selectedItems()
        paths = []
        for item in items:
            quest_name = item.data(Qt.UserRole)
            quest_path = self.path / quest_name / "quest.yaml"

            if not quest_path.is_file():
                QtWidgets.QErrorMessage.showMessage(
                    "Cannot delete quest {} as source file does not exist!".format(quest_name)
                )
                return

            paths += [quest_path]

        # Show confirmation dialog before deleting
        path_str = "\n".join(str(x.parent) for x in paths)
        confirm_question = "Are you sure you want to delete the following quests?\n" + path_str
        confirmed = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            confirm_question
        )
        if confirmed != QtWidgets.QMessageBox.Yes:
            return

        # Delete and post events for each file
        for quest_path in paths:
            quest_dir = quest_path.parent
            shutil.rmtree(quest_dir)
            rel_path = quest_dir.relative_to(self.path)
            QtCore.QCoreApplication.postEvent(
                QtCore.QCoreApplication.instance(),
                ObjectDeletedEvent("Quest", str(rel_path))
            )

        # Reload widget after deletion
        self.load(self.path)
