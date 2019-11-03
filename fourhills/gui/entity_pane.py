import os
from PyQt5 import QtWidgets

from fourhills import Npc, StatBlock


class EntityPane(QtWidgets.QWidget):

    def __init__(self, entity_type, entity_file, setting, parent=None):
        super().__init__(parent)

        self.entity_type = entity_type
        self.entity_file = entity_file
        self.setting = setting

        # Give self a VBoxLayout for components
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        name = os.path.basename(entity_file).split(".")[0]
        if entity_type == "NPC":
            self.entity = Npc.from_name(name, setting)
            self.layout.addWidget(self.create_npc_widget(self.entity))
        elif entity_type == "Monster":
            # Statblock contains all monster attributes, so use directly
            self.entity = StatBlock.from_name(name, setting)
            self.layout.addWidget(self.create_monster_widget(self.entity))
        else:
            self.entity = entity_type
            self.layout.addWidget(self.create_unknown_entity_widget(entity_file))

    def create_npc_widget(self, entity, parent=None):

        tab_widget = QtWidgets.QTabWidget(parent)

        info_edit = QtWidgets.QTextEdit(tab_widget)
        summary = entity.summary_info()
        character = entity.character_info()
        info = summary + character
        info_edit.setText("\n".join(info))
        info_edit.setReadOnly(True)
        tab_widget.addTab(info_edit, "Info")

        stats_edit = QtWidgets.QTextEdit(tab_widget)
        stats_edit.setText("\n".join(entity.battle_info()))
        stats_edit.setReadOnly(True)
        tab_widget.addTab(stats_edit, "Stats")

        return tab_widget

    def create_monster_widget(self, entity, parent=None):
        stats_edit = QtWidgets.QTextEdit(parent)
        stats_edit.setText("\n".join(entity.battle_info()))
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
