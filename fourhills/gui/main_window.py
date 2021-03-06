"""Main window for Fourhills GUI"""

from functools import partial
from pathlib import Path
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
import sys

from fourhills import Setting
from fourhills.exceptions import FourhillsSettingStructureError
from fourhills.gui.panes import (
    EntityPane,
    EntityListPane,
    LocationPane,
    LocationTreePane,
    NotePane,
    NoteTreePane,
    PartyPane,
    PartyListPane,
    QuestPane,
    QuestListPane,
)
from fourhills.gui.events import AnchorClickedEventFilter
from fourhills.gui.utils import Config
from fourhills.gui.widgets import WorkspaceTabWidget


class MainWindow(QtWidgets.QMainWindow):

    BASE_TITLE = "FourHills GUI"

    setting = None
    world_dir = None

    location_pane = None
    note_pane = None
    npc_pane = None
    monsters_pane = None
    party_pane = None
    quests_pane = None

    def __init__(self):
        super().__init__()

        # Basic window construction
        self.setObjectName("MainWindow")
        self.resize(800, 600)

        self.mdi_areas = []
        self.centralwidget = WorkspaceTabWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        # Create and set icon
        if getattr(sys, "frozen", False):
            icon_path = Path(sys.executable).parent / "resources" / "icon.png"
        else:
            icon_path = Path(__file__).parent / "resources" / "icon.png"
        self.setWindowIcon(QtGui.QIcon(str(icon_path)))

        # Root layout creation
        self.root_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.root_layout.setObjectName("root_layout")

        # Populate with starting panes
        self.create_location_pane(area=Qt.LeftDockWidgetArea)
        self.create_note_pane(area=Qt.LeftDockWidgetArea)
        self.create_party_pane(area=Qt.RightDockWidgetArea)
        self.create_npc_pane(area=Qt.RightDockWidgetArea)
        self.create_monsters_pane(area=Qt.RightDockWidgetArea)

        # Create actions, then menu bar using those actions
        self.create_actions()
        self.create_menu_bar()

        # Create errors to live permanently, so user can hide them from
        # appearing if desired
        self.create_error_boxes()

        # Final window setup
        self.setCentralWidget(self.centralwidget)
        self.setWindowState(Qt.WindowMaximized)

        # Check if there's a world to open already
        last_opened = Config.last_opened()
        if last_opened is not None:
            self.open_world(event=None, world_path=last_opened)

    def _show_docked_pane(self, pane, area=None):
        if area is None:
            self.addDockWidget(Qt.RightDockWidgetArea, pane)
            pane.setFloating(True)
        else:
            self.addDockWidget(area, pane)

    def create_location_pane(self, checked=False, area=None):
        if self.location_pane is None or not self.location_pane.isVisible():
            self.location_pane = LocationTreePane("Locations", self)
            self._show_docked_pane(self.location_pane, area)
            if hasattr(self, "setting") and self.setting is not None:
                self.location_pane.load(self.setting.world_dir)
            self.location_pane.widget().itemActivated.connect(self.on_location_activated)

    def create_note_pane(self, checked=False, area=None):
        if self.note_pane is None or not self.note_pane.isVisible():
            self.note_pane = NoteTreePane("GM Notes", self)
            self._show_docked_pane(self.note_pane, area)
            if hasattr(self, "setting") and self.setting is not None:
                self.note_pane.load(self.setting.notes_dir)
            self.note_pane.widget().itemActivated.connect(self.on_note_activated)

    def create_npc_pane(self, checked=False, area=None):
        if self.npc_pane is None or not self.npc_pane.isVisible():
            self.npc_pane = EntityListPane("NPCs", "NPC", self)
            self._show_docked_pane(self.npc_pane, area)
            if hasattr(self, "setting") and self.setting is not None:
                self.npc_pane.load(self.setting.npcs_dir)
            self.npc_pane.entity_list.itemActivated.connect(self.on_entity_activated)

    def create_monsters_pane(self, checked=False, area=None):
        if self.monsters_pane is None or not self.monsters_pane.isVisible():
            self.monsters_pane = EntityListPane("Monsters", "Monster", self)
            self._show_docked_pane(self.monsters_pane, area)
            if hasattr(self, "setting") and self.setting is not None:
                self.monsters_pane.load(self.setting.monsters_dir)
            self.monsters_pane.entity_list.itemActivated.connect(self.on_entity_activated)

    def create_party_pane(self, checked=False, area=None):
        if self.party_pane is None or not self.party_pane.isVisible():
            self.party_pane = PartyListPane("Party", self)
            self._show_docked_pane(self.party_pane, area)
            if hasattr(self, "setting") and self.setting is not None:
                self.party_pane.load(self.setting.parties_dir)
            self.party_pane.party_list.itemActivated.connect(self.on_party_activated)

    def create_quests_pane(self, checked=False, area=None):
        if self.quests_pane is None or not self.quests_pane.isVisible():
            self.quests_pane = QuestListPane("Quests", self)
            self._show_docked_pane(self.quests_pane, area)
            if hasattr(self, "setting") and self.setting is not None:
                self.quests_pane.load(self.setting.quest_dir)
            self.quests_pane.quest_list.itemActivated.connect(self.on_quest_activated)

    def create_actions(self):
        # File menu actions
        self.create_world_action = QtWidgets.QAction("&New World", self)
        self.create_world_action.setStatusTip("Create a new world")
        self.create_world_action.setShortcut("Ctrl+N")
        self.create_world_action.triggered.connect(self.create_world)

        self.open_world_action = QtWidgets.QAction("&Open World", self)
        self.open_world_action.setStatusTip("Open an existing world (fh_setting.yaml)")
        self.open_world_action.setShortcut("Ctrl+O")
        self.open_world_action.triggered.connect(self.open_world)

        self.exit_program_action = QtWidgets.QAction("Exit Fourhills", self)
        self.exit_program_action.setStatusTip("Exit Fourhills program")
        self.exit_program_action.triggered.connect(lambda x: QtWidgets.QApplication.quit())

        # View menu actions
        self.view_location_action = QtWidgets.QAction("&Locations", self)
        self.view_location_action.setStatusTip("View tree of locations within the world")
        self.view_location_action.triggered.connect(self.create_location_pane)

        self.view_npc_action = QtWidgets.QAction("&NPCs", self)
        self.view_npc_action.setStatusTip("View list of npcs within the world")
        self.view_npc_action.triggered.connect(self.create_npc_pane)

        self.view_monster_action = QtWidgets.QAction("&Monsters", self)
        self.view_monster_action.setStatusTip("View list of monsters within the world")
        self.view_monster_action.triggered.connect(self.create_monsters_pane)

        self.view_notes_action = QtWidgets.QAction("&GM Notes", self)
        self.view_notes_action.setStatusTip("View list of GM notes")
        self.view_notes_action.triggered.connect(self.create_note_pane)

        self.view_parties_action = QtWidgets.QAction("&Parties", self)
        self.view_parties_action.setStatusTip("View list of parties within the world")
        self.view_parties_action.triggered.connect(self.create_party_pane)

        self.view_quests_action = QtWidgets.QAction("&Quests", self)
        self.view_quests_action.setStatusTip("View list of quests")
        self.view_quests_action.triggered.connect(self.create_quests_pane)

    def create_menu_bar(self):
        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction(self.create_world_action)
        self.file_menu.addAction(self.open_world_action)
        self.file_menu.addSeparator()
        self.recent_worlds_menu = self.file_menu.addMenu("&Recent Worlds")
        self.update_recent_worlds_menu()
        self.file_menu.addAction(self.exit_program_action)

        self.view_menu = self.menuBar().addMenu("&View")
        self.view_menu.addAction(self.view_location_action)
        self.view_menu.addAction(self.view_npc_action)
        self.view_menu.addAction(self.view_monster_action)
        self.view_menu.addAction(self.view_notes_action)
        self.view_menu.addAction(self.view_parties_action)
        self.view_menu.addAction(self.view_quests_action)

    def update_recent_worlds_menu(self):
        self.recent_worlds_menu.clear()
        for world in Config.get_recent_worlds():
            if world.parent == self.world_dir:
                continue
            act = self.recent_worlds_menu.addAction(str(world))
            act.triggered.connect(partial(self.open_world, event=None, world_path=world))

    def create_error_boxes(self):
        self.world_open_error = QtWidgets.QErrorMessage(self)
        self.anchor_click_error = QtWidgets.QErrorMessage(self)
        self.note_open_error = QtWidgets.QErrorMessage(self)

    def on_entity_activated(self, event):
        # Get entity information and construct widget
        entity_type, entity_file = event.data(Qt.UserRole)
        self.open_entity(entity_type, entity_file)

    def open_entity(self, entity_type, entity_file):
        # Present error message if entity is not real
        try:
            entity_widget = EntityPane(entity_type, entity_file, self.setting, self)
        except FourhillsSettingStructureError as fsse:
            QtWidgets.QErrorMessage(self).showMessage("\n".join(fsse.args))
            return

        # Create a new Mdi window with the entity information
        sub_window = QtWidgets.QMdiSubWindow(self.centralwidget)
        sub_window.setWidget(entity_widget)
        sub_window.setAttribute(Qt.WA_DeleteOnClose)
        sub_window.setWindowTitle(entity_widget.title)

        self.centralwidget.current_mdi_area().addSubWindow(sub_window)
        sub_window.show()
        sub_window.resize(400, 400)

    def on_location_activated(self, event, column):
        # Figure out relative path to the opened location
        path = Path(".")
        item = event
        directories = [item.text(0)]
        while item.parent() is not None:
            directories += [item.parent().text(0)]
            item = item.parent()
        directories.reverse()
        for directory in directories:
            path = path / directory
        self.open_location(path)

    def open_location(self, path):
        # Present error message if location is not real
        try:
            location_widget = LocationPane(path, self.setting, self)
        except FourhillsSettingStructureError as fsse:
            QtWidgets.QErrorMessage(self).showMessage("\n".join(fsse.args))
            return

        # Create a new Mdi window with the location information
        sub_window = QtWidgets.QMdiSubWindow(self.centralwidget)
        sub_window.setWidget(location_widget)
        sub_window.setAttribute(Qt.WA_DeleteOnClose)
        sub_window.setWindowTitle(location_widget.title)

        self.centralwidget.current_mdi_area().addSubWindow(sub_window)
        sub_window.show()
        sub_window.resize(400, 400)

    def on_note_activated(self, event, column):
        # Figure out relative path to the opened note
        path = Path(".")
        item = event
        directories = [item.text(0)]
        while item.parent() is not None:
            directories += [item.parent().text(0)]
            item = item.parent()
        directories.reverse()
        for directory in directories:
            path = path / directory
        self.open_note(path)

    def open_note(self, path):
        # Check if path is a directory
        if (self.setting.notes_dir / path).is_dir():
            return

        # Check path is a markdown file
        abs_path = self.setting.notes_dir / path
        if not str(path).endswith(".md"):
            self.note_open_error.showMessage(
                f"Cannot open path {abs_path} as note. Only Markdown files "
                "are supported as GM notes."
            )
            return

        if not abs_path.is_file():
            self.note_open_error.showMessage(
                f"Cannot open path {abs_path} as it is not a file."
            )
            return

        note_widget = NotePane(path, self.setting, self)

        # Create a new Mdi window with the location information
        sub_window = QtWidgets.QMdiSubWindow(self.centralwidget)
        sub_window.setWidget(note_widget)
        sub_window.setAttribute(Qt.WA_DeleteOnClose)
        sub_window.setWindowTitle(note_widget.title)

        self.centralwidget.current_mdi_area().addSubWindow(sub_window)
        sub_window.show()
        sub_window.resize(400, 400)

    def on_party_activated(self, event):
        party_file = event.data(Qt.UserRole)
        self.open_party(party_file)

    def open_party(self, party):
        # Present error message if party is not real
        try:
            party_widget = PartyPane(party, self.setting, self)
        except FourhillsSettingStructureError as fsse:
            QtWidgets.QErrorMessage(self).showMessage("\n".join(fsse.args))
            return

        # Create a new Mdi window with the entity information
        sub_window = QtWidgets.QMdiSubWindow(self.centralwidget)
        sub_window.setWidget(party_widget)
        sub_window.setAttribute(Qt.WA_DeleteOnClose)
        sub_window.setWindowTitle(party_widget.title)

        self.centralwidget.current_mdi_area().addSubWindow(sub_window)
        sub_window.show()
        sub_window.resize(400, 400)

    def on_quest_activated(self, event):
        # Get quest information and construct widget
        quest_file = event.data(Qt.UserRole)
        self.open_quest(quest_file)

    def open_quest(self, quest):
        # Present error message if quest is not real
        try:
            quest_widget = QuestPane(quest, self.setting, self)
        except FourhillsSettingStructureError as fsse:
            QtWidgets.QErrorMessage(self).showMessage("\n".join(fsse.args))
            return

        # Create a new Mdi window with the entity information
        sub_window = QtWidgets.QMdiSubWindow(self.centralwidget)
        sub_window.setWidget(quest_widget)
        sub_window.setAttribute(Qt.WA_DeleteOnClose)
        sub_window.setWindowTitle(quest_widget.title)

        self.centralwidget.current_mdi_area().addSubWindow(sub_window)
        sub_window.show()
        sub_window.resize(400, 400)

    def on_anchor_clicked(self, event):
        # Work out the type of link clicked
        parts = event.url.url().split("://")
        event_type = parts[0]
        if event_type == "npc":
            self.open_entity("NPC", parts[1])
        elif event_type == "monster":
            self.open_entity("Monster", parts[1])
        elif event_type == "location":
            self.open_location(Path(*parts[1:]))
        elif event_type == "note":
            self.open_note(Path(*parts[1:]))
        elif event_type == "quest":
            self.open_quest(parts[1])
        elif event_type == "party":
            self.open_party(parts[1])
        else:
            self.anchor_click_error.showMessage(
                f"Unknown window type requested: {event_type}"
            )
            return

    def create_world(self, event):
        """User has requested a new world, so touch all the files and copy templates"""
        # Get path of new world from user
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select directory for new world",
            ".",
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        if not folder_name:
            # User cancelled
            return

        world_path = Path(folder_name)
        # Create all required folders and fh_setting.yaml
        for dir_name in Setting.DIRNAMES.values():
            create_path = world_path / dir_name
            create_path.mkdir()
        setting_path = world_path / "fh_setting.yaml"
        setting_path.touch()

        # Open new world
        self.open_world(None, world_path=setting_path)

    def open_world(self, event, world_path: Path = None):
        """User has requested opening a world, so find fh_setting.yaml"""
        # Ignore filter used to select file
        if not world_path:
            world_file, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Open World (fh_setting.yaml)",
                ".",
                "World Files (*.yaml)"
            )
            if not world_file:
                # User cancelled selection
                return
            world_path = Path(world_file)

        # Close all open windows before load
        self.centralwidget.clear()

        # Check world file is a fh_setting.yaml file
        if not self.load(world_path):
            # Give user an error dialog and return
            self.world_open_error.showMessage(
                f"The file selected was not a valid world file: {world_path}. "
                "Valid world files must be named \"fh_setting.yaml\" and contain a particular "
                "directory structure."
            )
            Config.remove_recent_world(world_path)
            self.update_recent_worlds_menu()
            return

        # Save world to recent worlds list
        Config.add_recent_world(world_path)
        self.update_recent_worlds_menu()

        # Save world to last opened
        Config.set_last_opened(world_path)

    def load(self, path) -> bool:
        world_dir = Path(path).parent
        setting = Setting(base_path=world_dir)
        if setting.root is None:
            return False
        self.setting = setting
        self.world_dir = world_dir
        self.setWindowTitle(self.BASE_TITLE + f" ({path})")
        if self.location_pane is not None:
            self.location_pane.load(self.setting.world_dir)
        if self.note_pane is not None:
            self.note_pane.load(self.setting.notes_dir)
        if self.npc_pane is not None:
            self.npc_pane.load(self.setting.npcs_dir)
        if self.monsters_pane is not None:
            self.monsters_pane.load(self.setting.monsters_dir)
        if self.quests_pane is not None:
            self.quests_pane.load(self.setting.quest_dir)
        if self.party_pane is not None:
            self.party_pane.load(self.setting.parties_dir)

        return True


def main():
    import sys
    app = QtWidgets.QApplication([])
    window = MainWindow()

    # Connect all anchor clicked signals to main window
    anchorFilter = AnchorClickedEventFilter.get_filter()
    anchorFilter.anchorClicked.connect(window.on_anchor_clicked)

    window.show()
    app.setApplicationName(MainWindow.BASE_TITLE)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
