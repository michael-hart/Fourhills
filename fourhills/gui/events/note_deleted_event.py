from PyQt5 import QtCore


class NoteDeletedEvent(QtCore.QEvent):

    EVENT_TYPE = None

    @staticmethod
    def registeredEventType():
        if NoteDeletedEvent.EVENT_TYPE is None:
            NoteDeletedEvent.EVENT_TYPE = QtCore.QEvent.registerEventType()
        return NoteDeletedEvent.EVENT_TYPE

    def __init__(self, note_path):
        super().__init__(NoteDeletedEvent.registeredEventType())
        self.note_path = note_path
