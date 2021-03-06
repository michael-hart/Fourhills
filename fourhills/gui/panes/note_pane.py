"""Definition for note pane, giving GM notes in Markdown format"""

import markdown
from pathlib import Path
from PyQt5 import QtWidgets

from fourhills import Setting
from fourhills.gui.events import ObjectDeletedEventFilter, ObjectRenamedEventFilter
from fourhills.gui.widgets import LinkingBrowser


class NotePane(QtWidgets.QWidget):

    def __init__(self, rel_path: Path, setting: Setting, parent=None):
        super().__init__(parent)

        self.rel_path = rel_path
        self.setting = setting

        # Create events for note renaming and deleting
        renameFilter = ObjectRenamedEventFilter.get_filter()
        renameFilter.objectRenamed.connect(self.on_note_renamed)
        deleteFilter = ObjectDeletedEventFilter.get_filter()
        deleteFilter.objectDeleted.connect(self.on_note_deleted)

        # Give self a VBoxLayout for components
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # self.location = Location.from_name(rel_path, setting)
        self.layout.addWidget(self.create_note_widget(self.rel_path, self.setting, self))

    def create_note_widget(self, rel_path: Path, setting: Setting, parent=None):
        note_path = setting.notes_dir / rel_path
        self.note_widget = LinkingBrowser(note_path, self.render_note, parent=parent)

        # Set window title depending on if file has changed or not
        self.note_widget.fileIsDifferent.connect(
            lambda: self.parent().setWindowTitle(self.title + "*")
        )
        self.note_widget.fileIsSame.connect(
            lambda: self.parent().setWindowTitle(self.title)
        )

        return self.note_widget

    def render_note(self, note_path):
        if not note_path.is_file():
            return ""
        with open(note_path) as f:
            md_contents = f.read()
        return markdown.markdown(md_contents)

    @property
    def title(self):
        # Get last three parts of a note
        cut_path = Path(*self.rel_path.parts[-3:])
        return str(cut_path) + " (Note)"

    # Rename/delete handlers

    def on_note_renamed(self, event):
        if event.object_type == "Note" and self.rel_path == event.old_object:
            self.rel_path = event.new_object
            note_path = self.setting.notes_dir / self.rel_path
            self.note_widget.edit_path = note_path

            # Update window title
            self.parent().setWindowTitle(self.title)

    def on_note_deleted(self, event):
        if event.object_type == "Note" and self.rel_path == event.object_name:
            self.parent().close()
