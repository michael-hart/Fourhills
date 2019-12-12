from PyQt5 import QtCore


class ObjectRenamedEvent(QtCore.QEvent):

    EVENT_TYPE = None

    @staticmethod
    def registeredEventType():
        if ObjectRenamedEvent.EVENT_TYPE is None:
            ObjectRenamedEvent.EVENT_TYPE = QtCore.QEvent.registerEventType()
        return ObjectRenamedEvent.EVENT_TYPE

    def __init__(self, object_type, old_object, new_object):
        super().__init__(ObjectRenamedEvent.registeredEventType())
        self.object_type = object_type
        self.old_object = old_object
        self.new_object = new_object
