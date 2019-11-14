from PyQt5 import QtCore


class NoteRenamedEvent(QtCore.QEvent):

    EVENT_TYPE = None

    @staticmethod
    def registeredEventType():
        if NoteRenamedEvent.EVENT_TYPE is None:
            NoteRenamedEvent.EVENT_TYPE = QtCore.QEvent.registerEventType()
        return NoteRenamedEvent.EVENT_TYPE

    def __init__(self, old_note_path, new_note_path):
        super().__init__(NoteRenamedEvent.registeredEventType())
        self.old_note_path = old_note_path
        self.new_note_path = new_note_path
