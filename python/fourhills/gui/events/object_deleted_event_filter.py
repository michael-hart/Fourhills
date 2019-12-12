from PyQt5 import QtCore
from fourhills.gui.events.object_deleted_event import ObjectDeletedEvent


class ObjectDeletedEventFilter(QtCore.QObject):

    objectDeleted = QtCore.pyqtSignal(ObjectDeletedEvent)

    def eventFilter(self, obj, event):
        if event and type(event) is ObjectDeletedEvent:
            self.objectDeleted.emit(event)
            return True
        return QtCore.QObject.eventFilter(self, obj, event)

    @staticmethod
    def get_filter():
        if not hasattr(ObjectDeletedEventFilter, "_filter"):
            core_app = QtCore.QCoreApplication.instance()
            _filter = ObjectDeletedEventFilter(core_app)
            core_app.installEventFilter(_filter)
            ObjectDeletedEventFilter._filter = _filter
        return ObjectDeletedEventFilter._filter
