from PyQt5 import QtCore
from fourhills.gui.events.entity_renamed_event import EntityRenamedEvent


class EntityRenamedEventFilter(QtCore.QObject):

    entityRenamed = QtCore.pyqtSignal(EntityRenamedEvent)

    def eventFilter(self, obj, event):
        if event and type(event) is EntityRenamedEvent:
            self.entityRenamed.emit(event)
            return True
        return QtCore.QObject.eventFilter(self, obj, event)

    @staticmethod
    def get_filter():
        if not hasattr(EntityRenamedEventFilter, "_filter"):
            core_app = QtCore.QCoreApplication.instance()
            _filter = EntityRenamedEventFilter(core_app)
            core_app.installEventFilter(_filter)
            EntityRenamedEventFilter._filter = _filter
        return EntityRenamedEventFilter._filter
