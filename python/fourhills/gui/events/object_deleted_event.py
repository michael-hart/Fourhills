from PyQt5 import QtCore


class ObjectDeletedEvent(QtCore.QEvent):

    EVENT_TYPE = None

    @staticmethod
    def registeredEventType():
        if ObjectDeletedEvent.EVENT_TYPE is None:
            ObjectDeletedEvent.EVENT_TYPE = QtCore.QEvent.registerEventType()
        return ObjectDeletedEvent.EVENT_TYPE

    def __init__(self, object_type, object_name):
        super().__init__(ObjectDeletedEvent.registeredEventType())
        self.object_type = object_type
        self.object_name = object_name
