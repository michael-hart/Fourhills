from PyQt5 import QtCore


class EntityDeletedEvent(QtCore.QEvent):

    EVENT_TYPE = None

    @staticmethod
    def registeredEventType():
        if EntityDeletedEvent.EVENT_TYPE is None:
            EntityDeletedEvent.EVENT_TYPE = QtCore.QEvent.registerEventType()
        return EntityDeletedEvent.EVENT_TYPE

    def __init__(self, entity_type, entity_name):
        super().__init__(EntityDeletedEvent.registeredEventType())
        self.entity_type = entity_type
        self.entity_name = entity_name
