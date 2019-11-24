"""Definition for a quest pane, giving details about a possible quest"""

import jinja2
import markdown
from pathlib import Path
from PyQt5 import QtWidgets

from fourhills import Setting
from fourhills.dataclasses import Quest
from fourhills.gui.widgets import LinkingBrowser
from fourhills.gui.events import ObjectDeletedEventFilter, ObjectRenamedEventFilter


class QuestPane(QtWidgets.QWidget):

    def __init__(self, name: str, setting: Setting, parent=None):
        super().__init__(parent)

        self.name = name
        self.setting = setting

        # Jinja template initialisation
        jinja_env = jinja2.Environment(
            loader=jinja2.PackageLoader('fourhills', package_path='gui/templates')
        )

        self.quest_template = jinja_env.get_template("quest_info.j2")

        # Create events for quest renaming and deleting
        renameFilter = ObjectRenamedEventFilter.get_filter()
        renameFilter.objectRenamed.connect(self.on_quest_renamed)
        deleteFilter = ObjectDeletedEventFilter.get_filter()
        deleteFilter.objectDeleted.connect(self.on_quest_deleted)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.create_quest_widget(self.name, self.setting, self))

    def create_quest_widget(self, name: str, setting: Setting, parent=None):
        self.tab_widget = QtWidgets.QTabWidget(parent)

        quest_path = Quest.get_quest_path(Path(name), setting)
        description_path = Quest.get_description_path(Path(name), setting)

        if not description_path.is_file():
            description_path.touch()

        self.quest_widget = LinkingBrowser(quest_path, self.render_quest, parent=parent)
        self.description_widget = LinkingBrowser(
            description_path,
            self.render_description,
            parent=parent
        )

        self.quest_tab = self.tab_widget.addTab(self.quest_widget, "Quest")
        self.description_tab = self.tab_widget.addTab(self.description_widget, "Description")

        # Watch for file changes and add asterisks
        self.quest_widget.fileIsDifferent.connect(
            lambda: self.tab_widget.setTabText(self.quest_tab, "Quest*")
        )
        self.quest_widget.fileIsSame.connect(
            lambda: self.tab_widget.setTabText(self.quest_tab, "Quest")
        )
        self.description_widget.fileIsDifferent.connect(
            lambda: self.tab_widget.setTabText(self.description_tab, "Description*")
        )
        self.description_widget.fileIsSame.connect(
            lambda: self.tab_widget.setTabText(self.description_tab, "Description")
        )

        return self.tab_widget

    def render_quest(self, quest_path):
        quest = Quest.from_name(quest_path.parent.name, self.setting)
        return self.quest_template.render(quest=quest)

    def render_description(self, description_path):
        with open(description_path) as f:
            md_contents = f.read()
        return markdown.markdown(md_contents)

    @property
    def title(self):
        return str(Quest.from_name(Path(self.name), self.setting))

    # Rename/delete handlers

    def on_quest_renamed(self, event):
        if event.object_type == "Quest" and self.name == event.old_object:
            self.name = event.new_object
            quest_path = Quest.get_quest_path(self.name, self.setting)
            description_path = Quest.get_description_path(self.name, self.setting)
            self.quest_widget.edit_path = quest_path
            self.description_widget.edit_path = description_path

            # Update window title
            self.parent().setWindowTitle(self.title)

    def on_quest_deleted(self, event):
        if event.object_type == "Quest" and self.name == event.object_name:
            self.parent().close()
