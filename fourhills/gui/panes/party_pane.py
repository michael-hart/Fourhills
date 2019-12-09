import jinja2
from pathlib import Path
from PyQt5 import QtWidgets

from fourhills.dataclasses import Party
from fourhills.gui.widgets import LinkingBrowser
from fourhills.gui.events import ObjectRenamedEventFilter, ObjectDeletedEventFilter


class PartyPane(QtWidgets.QWidget):

    def __init__(self, party_name, setting, parent=None):
        super().__init__(parent)

        self.party_name = party_name
        self.setting = setting

        # Jinja template initialisation
        jinja_env = jinja2.Environment(
            loader=jinja2.PackageLoader('fourhills', package_path='gui/templates')
        )

        self.party_info_template = jinja_env.get_template("party_info.j2")

        # Create events for party renaming and deleting
        renameFilter = ObjectRenamedEventFilter.get_filter()
        renameFilter.objectRenamed.connect(self.on_party_renamed)
        deleteFilter = ObjectDeletedEventFilter.get_filter()
        deleteFilter.objectDeleted.connect(self.on_party_deleted)

        # Give self a VBoxLayout for components
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.create_party_widget(party_name, self.setting)

    def create_party_widget(self, party_name, setting):
        party_path = Party.absolute_path(party_name, setting)

        self.party_edit = LinkingBrowser(party_path, self.render_party)
        self.party_edit.fileIsSame.connect(
            lambda: self.parent().setWindowTitle(self.unmodified_title())
        )
        self.party_edit.fileIsDifferent.connect(
            lambda: self.parent().setWindowTitle(self.modified_title())
        )
        self.layout.addWidget(self.party_edit)

    def unmodified_title(self):
        return self.title

    def modified_title(self):
        return "{}* (Party)".format(self.party_name)

    @property
    def title(self):
        return "{} (Party)".format(self.party_name)

    def on_party_renamed(self, event):
        # Check if the object is the same as loaded in this window
        if event.old_object != self.entity_name or event.object_type != "Party":
            return

        self.party_name = event.new_object
        party_path = Party.absolute_path(self.party_name, self.setting)
        self.party_edit.edit_path = party_path
        self.parent().setWindowTitle(self.title)

    def on_party_deleted(self, event):
        # Check if the object is the same as loaded in this window
        if event.object_name != self.party_name or event.object_type != "Party":
            return
        # Delete the parent MdiSubWindow
        self.parent().close()

    def render_party(self, party_path: Path):
        party = Party.from_name(party_path.stem, self.setting)
        return self.party_info_template.render(party=party)
