import jinja2
from PyQt5 import QtWidgets

from fourhills import Npc, StatBlock
from fourhills.gui.events import EntityRenamedEventFilter, EntityDeletedEventFilter


class EntityPane(QtWidgets.QWidget):

    def __init__(self, entity_type, entity_file, setting, parent=None):
        super().__init__(parent)

        self.entity_type = entity_type
        self.entity_file = entity_file
        self.setting = setting

        # Jinja template initialisation
        jinja_env = jinja2.Environment(
            loader=jinja2.PackageLoader('fourhills', package_path='gui/templates')
        )

        self.battle_info_template = jinja_env.get_template("battle_info.j2")
        self.character_info_template = jinja_env.get_template("character_info.j2")

        # Create events for entity renaming and deleting
        renameFilter = EntityRenamedEventFilter.get_filter()
        renameFilter.entityRenamed.connect(self.on_entity_renamed)
        deleteFilter = EntityDeletedEventFilter.get_filter()
        deleteFilter.entityDeleted.connect(self.on_entity_deleted)

        # Give self a VBoxLayout for components
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.set_entity(entity_type, entity_file)
        self.create_entity_widget(entity_type, self.entity)

    def create_entity_widget(self, entity_type, entity):
        if entity_type == "NPC":
            self.layout.addWidget(self.create_npc_widget(entity))
        elif entity_type == "Monster":
            self.layout.addWidget(self.create_monster_widget(entity))
        else:
            self.layout.addWidget(self.create_unknown_entity_widget(entity))

    def set_entity(self, entity_type, entity_file):
        if entity_type == "NPC":
            self.entity = Npc.from_name(entity_file, self.setting)
        elif entity_type == "Monster":
            # Statblock contains all monster attributes, so use directly
            self.entity = StatBlock.from_name(entity_file, self.setting)
        else:
            self.entity = entity_file

    def create_npc_widget(self, entity, parent=None):

        tab_widget = QtWidgets.QTabWidget(parent)

        info_edit = QtWidgets.QTextEdit(tab_widget)
        info_edit.setText(self.character_info_template.render(npc=entity))
        info_edit.setReadOnly(True)
        tab_widget.addTab(info_edit, "Info")

        stats_edit = QtWidgets.QTextEdit(tab_widget)
        stats_edit.setText(self.battle_info_template.render(stats=entity.stats))
        stats_edit.setReadOnly(True)
        tab_widget.addTab(stats_edit, "Stats")

        return tab_widget

    def create_monster_widget(self, entity, parent=None):
        stats_edit = QtWidgets.QTextEdit(parent)
        stats_edit.setText(self.battle_info_template.render(stats=entity))
        stats_edit.setReadOnly(True)
        return stats_edit

    def create_unknown_entity_widget(self, entity_file, parent=None):
        # Component will be a QTextEdit containing raw YAML
        text_edit = QtWidgets.QTextEdit(parent)

        with open(self.entity_file, 'r') as entity:
            entity_text = entity.read()
        text_edit.setText(entity_text)
        return text_edit

    @property
    def title(self):
        if type(self.entity) == str:
            return self.entity + " (Unknown Entity)"
        else:
            return "{} ({})".format(self.entity.name, self.entity_type)

    def on_entity_renamed(self, event):
        # Check if the entity is the same as loaded in this window
        if event.old_entity != self.entity_file or event.entity_type != self.entity_type:
            return
        self.entity_file = event.new_entity
        self.set_entity(self.entity_type, self.entity_file)

    def on_entity_deleted(self, event):
        # Check if the entity is the same as loaded in this window
        if event.entity_name != self.entity_file or event.entity_type != self.entity_type:
            return
        # Delete the parent MdiSubWindow
        self.parent().close()
