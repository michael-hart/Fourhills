from PyQt5 import QtCore
from fourhills.gui.events.note_renamed_event import NoteRenamedEvent


class NoteRenamedEventFilter(QtCore.QObject):

    noteRenamed = QtCore.pyqtSignal(NoteRenamedEvent)

    def eventFilter(self, obj, event):
        if event and type(event) is NoteRenamedEvent:
            self.noteRenamed.emit(event)
            return True
        return QtCore.QObject.eventFilter(self, obj, event)

    @staticmethod
    def get_filter():
        if not hasattr(NoteRenamedEventFilter, "_filter"):
            core_app = QtCore.QCoreApplication.instance()
            _filter = NoteRenamedEventFilter(core_app)
            core_app.installEventFilter(_filter)
            NoteRenamedEventFilter._filter = _filter
        return NoteRenamedEventFilter._filter
