from PyQt5 import QtCore
from fourhills.gui.events.entity_deleted_event import EntityDeletedEvent


class EntityDeletedEventFilter(QtCore.QObject):

    entityDeleted = QtCore.pyqtSignal(EntityDeletedEvent)

    def eventFilter(self, obj, event):
        if event and type(event) is EntityDeletedEvent:
            self.entityDeleted.emit(event)
            return True
        return QtCore.QObject.eventFilter(self, obj, event)

    @staticmethod
    def get_filter():
        if not hasattr(EntityDeletedEventFilter, "_filter"):
            core_app = QtCore.QCoreApplication.instance()
            _filter = EntityDeletedEventFilter(core_app)
            core_app.installEventFilter(_filter)
            EntityDeletedEventFilter._filter = _filter
        return EntityDeletedEventFilter._filter
