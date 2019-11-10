from PyQt5 import QtCore


class EntityRenamedEvent(QtCore.QEvent):

    EVENT_TYPE = None

    @staticmethod
    def registeredEventType():
        if EntityRenamedEvent.EVENT_TYPE is None:
            EntityRenamedEvent.EVENT_TYPE = QtCore.QEvent.registerEventType()
        return EntityRenamedEvent.EVENT_TYPE

    def __init__(self, entity_type, old_entity, new_entity):
        super().__init__(EntityRenamedEvent.registeredEventType())
        self.entity_type = entity_type
        self.old_entity = old_entity
        self.new_entity = new_entity
