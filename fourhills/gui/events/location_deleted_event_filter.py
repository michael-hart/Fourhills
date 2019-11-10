from PyQt5 import QtCore
from fourhills.gui.events.location_deleted_event import LocationDeletedEvent


class LocationDeletedEventFilter(QtCore.QObject):

    locationDeleted = QtCore.pyqtSignal(LocationDeletedEvent)

    def eventFilter(self, obj, event):
        if event and type(event) is LocationDeletedEvent:
            self.locationDeleted.emit(event)
            return True
        return QtCore.QObject.eventFilter(self, obj, event)

    @staticmethod
    def get_filter():
        if not hasattr(LocationDeletedEventFilter, "_filter"):
            core_app = QtCore.QCoreApplication.instance()
            _filter = LocationDeletedEventFilter(core_app)
            core_app.installEventFilter(_filter)
            LocationDeletedEventFilter._filter = _filter
        return LocationDeletedEventFilter._filter
