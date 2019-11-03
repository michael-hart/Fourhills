"""Definition for content pane, which contains one or more other panes"""

import os

from PyQt5 import QtWidgets
from fourhills.gui.centre_pane import CentrePane
from fourhills.gui.location_pane import LocationPane
from fourhills.gui.monster_pane import MonsterPane
from fourhills.gui.npc_pane import NpcPane
from fourhills.gui.tab_result import TabResult
from fourhills.setting import Setting


class ContentPane(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = QtWidgets.QHBoxLayout()

        # Create setting and populate location list
        self.setting = Setting()
        if not self.setting.root:
            msg = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical,
                "Setting not found",
                "Could not load setting - please run program from a valid directory!",
                QtWidgets.QMessageBox.Ok
            )
            msg.exec_()
            return

        # Content pane is initialised with location pane and centre pane
        self.location_pane = LocationPane(self.setting)
        self.centre_pane = CentrePane()
        self.layout.addWidget(self.location_pane, 1)
        self.layout.addWidget(self.centre_pane, 2)

        # Add NPC and Monster panes as hidden
        self.npc_pane = NpcPane(self.setting)
        self.npc_pane.hide()
        self.monster_pane = MonsterPane(self.setting)
        self.monster_pane.hide()
        self.layout.addWidget(self.npc_pane, 1)
        self.layout.addWidget(self.monster_pane, 1)

        self.setLayout(self.layout)

        # Connect item activated event to switch centre pane contents
        self.location_pane.location_list.itemActivated.connect(self.on_location_activated)

        self.location_selected = None

    def on_location_activated(self, location):
        # Get the description.md from the given location
        location_text = location.text().replace("/", os.path.sep)
        self.location_selected = location_text
        description_path = os.path.join(self.setting.world_dir, location_text, "description.md")
        self.centre_pane.set_content(description_path)

    def show_monster_pane(self):
        if self.npc_pane.isVisible():
            self.npc_pane.hide()
        self.monster_pane.show()
        # Focus monster pane as it has been opened
        if not self.monster_pane.has_focus():
            self.monster_pane.handle_tab()

    def show_npc_pane(self):
        if self.monster_pane.isVisible():
            self.monster_pane.hide()
        self.npc_pane.show()
        # Focus NPC pane as it has been opened
        if not self.npc_pane.has_focus():
            self.npc_pane.handle_tab()

    def clear_additional_panes(self):
        self.monster_pane.hide()
        self.npc_pane.hide()
        if self.monster_pane.has_focus() or self.npc_pane.has_focus():
            self.location_pane.handle_tab()

    def has_focus(self):
        """Alternative to hasFocus which checks widget children for focus"""
        return (
            self.location_pane.has_focus() or
            (self.npc_pane.isVisible() and self.npc_pane.has_focus()) or
            (self.monster_pane.isVisible() and self.monster_pane.has_focus()) or
            self.centre_pane.has_focus()
        )

    def handle_tab(self, reverse=False):
        panes = [self.location_pane, self.centre_pane]
        if self.monster_pane.isVisible():
            panes += [self.monster_pane]
        if self.npc_pane.isVisible():
            panes += [self.npc_pane]
        if reverse:
            panes.reverse()

        for idx, pane in enumerate(panes):
            if pane.has_focus():
                result = pane.handle_tab(reverse)
                if result == TabResult.TabRemaining and pane == panes[-1]:
                    return TabResult.TabRemaining
                elif result == TabResult.TabRemaining:
                    panes[idx + 1].handle_tab(reverse)
                    return TabResult.TabConsumed
                elif result == TabResult.TabConsumed:
                    return TabResult.TabConsumed

        # If this point is reached, this pane does not currently have focus, so focus should be
        # given to the first component - or last in case of reverse
        panes[0].handle_tab(reverse)
        return TabResult.TabConsumed
