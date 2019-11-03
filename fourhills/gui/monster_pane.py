"""Definition for monsters pane, showing information about monsters at a location"""

import os
import glob
from PyQt5 import QtWidgets

from fourhills.gui.tab_result import TabResult


class MonsterPane(QtWidgets.QWidget):

    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.layout = QtWidgets.QVBoxLayout()

        # Vertically arranged to have a list of available monsters
        # and a text box containing monster info

        self.layout.addWidget(QtWidgets.QLabel("Monsters:"))

        self.monster_list = QtWidgets.QListWidget()
        self.layout.addWidget(self.monster_list, stretch=1)

        self.monster_info = QtWidgets.QTextEdit()
        self.monster_info.setReadOnly(True)
        self.layout.addWidget(self.monster_info, stretch=3)

        self.setLayout(self.layout)

        self.settings = settings
        self.populate_monsters()

        self.monster_list.itemActivated.connect(self.on_monster_activated)

    def populate_monsters(self):
        # Find all monster descriptions within the monsters directory
        monster_dir = self.settings.monsters_dir
        for monster_file in glob.glob(str(monster_dir / "*.yaml"), recursive=True):
            rel_path = os.path.relpath(monster_file, monster_dir)
            rel_path.replace(os.path.sep, "/")
            self.monster_list.addItem(rel_path)

        if self.monster_list.count():
            self.monster_list.setCurrentRow(0)

    def on_monster_activated(self, monster):
        monster_txt = monster.text().replace("/", os.path.sep)
        path = os.path.join(self.settings.monsters_dir, monster_txt)
        with open(path) as f:
            self.monster_info.setText(f.read())

    def has_focus(self):
        """Alternative to hasFocus which checks widget children for focus"""
        return self.monster_list.hasFocus() or self.monster_info.hasFocus()

    def handle_tab(self, reverse=False):
        controls = [self.monster_list, self.monster_info]
        if reverse:
            controls.reverse()

        for idx, control in enumerate(controls):
            if control.hasFocus():
                if control == controls[-1]:
                    return TabResult.TabRemaining
                else:
                    controls[idx + 1].setFocus()
                    return TabResult.TabConsumed

        # If no control has focus, set the default control
        controls[0].setFocus()
        return TabResult.TabConsumed
