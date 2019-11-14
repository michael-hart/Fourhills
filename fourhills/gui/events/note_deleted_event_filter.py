from PyQt5 import QtCore
from fourhills.gui.events.note_deleted_event import NoteDeletedEvent


class NoteDeletedEventFilter(QtCore.QObject):

    noteDeleted = QtCore.pyqtSignal(NoteDeletedEvent)

    def eventFilter(self, obj, event):
        if event and type(event) is NoteDeletedEvent:
            self.noteDeleted.emit(event)
            return True
        return QtCore.QObject.eventFilter(self, obj, event)

    @staticmethod
    def get_filter():
        if not hasattr(NoteDeletedEventFilter, "_filter"):
            core_app = QtCore.QCoreApplication.instance()
            _filter = NoteDeletedEventFilter(core_app)
            core_app.installEventFilter(_filter)
            NoteDeletedEventFilter._filter = _filter
        return NoteDeletedEventFilter._filter
