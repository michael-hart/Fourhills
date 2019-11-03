"""Definition for NPC pane, which shows information about NPCs at a location"""

import os
import glob
from PyQt5 import QtWidgets

from fourhills.gui.tab_result import TabResult


class NpcPane(QtWidgets.QWidget):

    def __init__(self, setting, **kwargs):
        super().__init__(**kwargs)
        self.layout = QtWidgets.QVBoxLayout()

        # Vertically arranged to have a list of available NPCs
        # and a text box containing NPC info

        self.layout.addWidget(QtWidgets.QLabel("NPCs:"))

        self.npc_list = QtWidgets.QListWidget()
        self.layout.addWidget(self.npc_list, stretch=1)

        self.npc_info = QtWidgets.QTextEdit()
        self.npc_info.setReadOnly(True)
        self.layout.addWidget(self.npc_info, stretch=3)

        self.setLayout(self.layout)

        self.settings = setting
        self.populate_npcs()

        self.npc_list.itemActivated.connect(self.on_npc_activated)

    def populate_npcs(self):
        # Find all NPC descriptions within the NPC directory
        npc_dir = self.settings.npcs_dir
        for npc_file in glob.glob(str(npc_dir / "*.yaml"), recursive=True):
            rel_path = os.path.relpath(npc_file, npc_dir)
            rel_path.replace(os.path.sep, "/")
            self.npc_list.addItem(rel_path)
        if self.npc_list.count():
            self.npc_list.setCurrentRow(0)

    def on_npc_activated(self, npc):
        npc_text = npc.text().replace("/", os.path.sep)
        path = os.path.join(self.settings.npcs_dir, npc_text)
        with open(path) as f:
            self.npc_info.setText(f.read())

    def has_focus(self):
        """Alternative to hasFocus which checks widget children for focus"""
        return self.npc_list.hasFocus() or self.npc_info.hasFocus()

    def handle_tab(self, reverse=False):
        controls = [self.npc_list, self.npc_info]
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
