from PyQt5 import QtCore
from fourhills.gui.events.object_renamed_event import ObjectRenamedEvent


class ObjectRenamedEventFilter(QtCore.QObject):

    objectRenamed = QtCore.pyqtSignal(ObjectRenamedEvent)

    def eventFilter(self, obj, event):
        if event and type(event) is ObjectRenamedEvent:
            self.objectRenamed.emit(event)
            return True
        return QtCore.QObject.eventFilter(self, obj, event)

    @staticmethod
    def get_filter():
        if not hasattr(ObjectRenamedEventFilter, "_filter"):
            core_app = QtCore.QCoreApplication.instance()
            _filter = ObjectRenamedEventFilter(core_app)
            core_app.installEventFilter(_filter)
            ObjectRenamedEventFilter._filter = _filter
        return ObjectRenamedEventFilter._filter
