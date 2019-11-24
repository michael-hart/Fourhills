from pathlib import Path
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
import shutil

from fourhills.gui.events import AnchorClickedEvent


class QuestListPane(QtWidgets.QDockWidget):

    path = None

    def __init__(self, title, parent=None):
        super().__init__(title, parent)

        self.centralwidget = QtWidgets.QWidget()
        self.setWidget(self.centralwidget)
        layout = QtWidgets.QVBoxLayout()
        self.centralwidget.setLayout(layout)

        self.quest_list = QtWidgets.QListWidget()
        self.quest_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.quest_list)

        # Allow user options for adding/renaming/deleting quests
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

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
        menu.addAction(f"Create Quest", self.create_quest)
        n_selected = len(self.quest_list.selectedItems())
        if n_selected == 1:
            menu.addAction(f"Rename Quest", self.rename_quest)
        if n_selected >= 1:
            menu.addAction(f"Delete Quest(s)", self.delete_quests)

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
