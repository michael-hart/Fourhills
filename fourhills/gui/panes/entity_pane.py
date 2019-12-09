import jinja2
from pathlib import Path
from PyQt5 import QtWidgets

from fourhills.dataclasses import Npc, StatBlock
from fourhills.exceptions import FourhillsExperienceLookupError
from fourhills.utils import cr_to_xp
from fourhills.gui.widgets import LinkingBrowser
from fourhills.gui.events import ObjectRenamedEventFilter, ObjectDeletedEventFilter


class EntityPane(QtWidgets.QWidget):

    def __init__(self, entity_type, entity_name, setting, parent=None):
        super().__init__(parent)

        self.entity_type = entity_type
        self.entity_name = entity_name
        self.setting = setting

        # Check that entity_type is valid and refuse it if not
        if entity_type not in ["Monster", "NPC"]:
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot create entity pane from unknown entity type {}".format(
                    entity_type
                )
            )
            self.parent().close()
            return

        # Jinja template initialisation
        jinja_env = jinja2.Environment(
            loader=jinja2.PackageLoader('fourhills', package_path='gui/templates')
        )
        jinja_env.globals.update(cr_to_xp=cr_to_xp)

        self.battle_info_template = jinja_env.get_template("battle_info.j2")
        self.character_info_template = jinja_env.get_template("character_info.j2")

        # Create events for entity renaming and deleting
        renameFilter = ObjectRenamedEventFilter.get_filter()
        renameFilter.objectRenamed.connect(self.on_entity_renamed)
        deleteFilter = ObjectDeletedEventFilter.get_filter()
        deleteFilter.objectDeleted.connect(self.on_entity_deleted)

        # Give self a VBoxLayout for components
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.create_entity_widget(entity_type, self.entity_name, self.setting)

    def create_entity_widget(self, entity_type, entity_name, setting):
        if entity_type == "NPC":
            entity_path = Npc.absolute_path(entity_name, setting)
            self.layout.addWidget(self.create_npc_widget(entity_path))
        elif entity_type == "Monster":
            entity_path = StatBlock.absolute_path(entity_name, setting)
            self.layout.addWidget(self.create_monster_widget(entity_path))

    def create_npc_widget(self, entity_path, parent=None):

        self.tab_widget = QtWidgets.QTabWidget(parent)

        self.info_edit = LinkingBrowser(entity_path, self.render_npc)
        self.stat_edit = LinkingBrowser(entity_path, self.render_npc_stat, editable=False)

        self.info_tab = self.tab_widget.addTab(self.info_edit, "Info")
        self.stat_tab = self.tab_widget.addTab(self.stat_edit, "Stats")

        self.info_edit.fileIsSame.connect(
            lambda: self.tab_widget.setTabText(self.info_tab, "Info")
        )
        self.info_edit.fileIsDifferent.connect(
            lambda: self.tab_widget.setTabText(self.info_tab, "Info*")
        )

        return self.tab_widget

    def create_monster_widget(self, entity_path, parent=None):
        self.stat_edit = LinkingBrowser(entity_path, self.render_monster_stat)
        self.stat_edit.fileIsSame.connect(
            lambda: self.parent().setWindowTitle(self.title)
        )
        self.stat_edit.fileIsDifferent.connect(
            lambda: self.parent().setWindowTitle(self.title + "*")
        )
        return self.stat_edit

    @property
    def title(self):
        return "{} ({})".format(self.entity_name, self.entity_type)

    def on_entity_renamed(self, event):
        # Check if the entity is the same as loaded in this window
        if event.old_object != self.entity_name or event.object_type != self.entity_type:
            return
        self.entity_name = event.new_object
        if self.entity_type == "NPC":
            entity_path = Npc.absolute_path(self.entity_name, self.setting)
            self.info_edit.edit_path = entity_path
            self.stat_edit.edit_path = entity_path

        elif self.entity_type == "Monster":
            entity_path = StatBlock.absolute_path(self.entity_name, self.setting)
            self.stat_edit.edit_path = entity_path
        self.parent().setWindowTitle(self.title)

    def on_entity_deleted(self, event):
        # Check if the entity is the same as loaded in this window
        if event.object_name != self.entity_name or event.object_type != self.entity_type:
            return
        # Delete the parent MdiSubWindow
        self.parent().close()

    def render_npc(self, entity_path: Path):
        npc = Npc.from_name(entity_path.stem, self.setting)
        return self.character_info_template.render(npc=npc)

    def render_npc_stat(self, entity_path: Path):
        npc = Npc.from_name(entity_path.stem, self.setting)
        try:
            npc.xp = f"{cr_to_xp(npc.stats.challenge)} XP"
        except FourhillsExperienceLookupError:
            npc.xp = "XP could not be calculated"
        return self.battle_info_template.render(stats=npc.stats)

    def render_monster_stat(self, entity_path: Path):
        monster = StatBlock.from_name(entity_path.stem, self.setting)
        try:
            monster.xp = f"{cr_to_xp(monster.challenge)} XP"
        except FourhillsExperienceLookupError:
            monster.xp = "XP could not be calculated"
        return self.battle_info_template.render(stats=monster)
