"""Main window for Fourhills GUI"""

import os
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from fourhills import Setting
from fourhills.gui.entity_list_pane import EntityListPane
from fourhills.gui.entity_pane import EntityPane


class MainWindow(QtWidgets.QMainWindow):

    BASE_TITLE = "FourHills GUI"

    def __init__(self):
        super().__init__()

        # Basic window construction
        self.setObjectName("MainWindow")
        self.resize(800, 600)
        self.centralwidget = QtWidgets.QMdiArea(self)
        self.centralwidget.setObjectName("centralwidget")

        # Root layout creation
        self.root_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.root_layout.setObjectName("root_layout")

        # Populate with starting panes
        self.npc_pane = EntityListPane("NPCs", "NPC", self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.npc_pane)
        self.npc_pane.widget().itemActivated.connect(self.on_entity_activated)

        self.monsters_pane = EntityListPane("Monsters", "Monster", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.monsters_pane)
        self.monsters_pane.widget().itemActivated.connect(self.on_entity_activated)

        # Create actions, then menu bar using those actions
        self.create_actions()
        self.create_menu_bar()

        # Create errors to live permanently, so user can hide them from
        # appearing if desired
        self.create_error_boxes()

        # Final window setup
        self.setCentralWidget(self.centralwidget)
        self.setWindowState(Qt.WindowMaximized)

    def create_actions(self):
        self.open_world_action = QtWidgets.QAction("&Open World", self)
        self.open_world_action.setStatusTip("Open an existing world (fh_setting.yaml)")
        self.open_world_action.setShortcut("Ctrl+O")
        self.open_world_action.triggered.connect(self.open_world)

    def create_menu_bar(self):
        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction(self.open_world_action)

    def create_error_boxes(self):
        self.world_open_error = QtWidgets.QErrorMessage(self)

    def on_entity_activated(self, event):
        # Get entity information and construct widget
        entity_type, entity_file = event.data(Qt.UserRole)
        entity_widget = EntityPane(entity_type, entity_file, self.setting, self)

        # Create a new Mdi window with the entity information
        sub_window = QtWidgets.QMdiSubWindow(self.centralwidget)
        sub_window.setWidget(entity_widget)
        sub_window.setAttribute(Qt.WA_DeleteOnClose)
        sub_window.setWindowTitle(entity_widget.title)

        self.centralwidget.addSubWindow(sub_window)
        sub_window.show()

    def open_world(self, event):
        """User has requested opening a world, so find fh_setting.yaml"""
        # Ignore filter used to select file
        world_file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open World (fh_setting.yaml)",
            ".",
            "World Files (*.yaml)"
        )
        if not world_file:
            # User cancelled selection
            return

        # Check world file is a fh_setting.yaml file
        if not self.load(world_file):
            # Give user an error dialog and return
            self.world_open_error.showMessage(
                f"The file selected was not a valid world file: {world_file}. "
                "Valid world files must be named \"fh_setting.yaml\" and contain a particular "
                "directory structure."
            )

    def load(self, path) -> bool:
        world_dir = Path(path).parent
        setting = Setting(base_path=world_dir)
        if setting.root is None:
            return False
        self.setting = setting
        self.world_dir = world_dir
        self.setWindowTitle(self.BASE_TITLE + f" ({path})")
        self.npc_pane.load(self.world_dir / "npcs")
        self.monsters_pane.load(self.world_dir / "monsters")
        return True


def main():
    import sys
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.setApplicationName(MainWindow.BASE_TITLE)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
