from PyQt5 import QtCore
from fourhills.gui.events.location_renamed_event import LocationRenamedEvent


class LocationRenamedEventFilter(QtCore.QObject):

    locationRenamed = QtCore.pyqtSignal(LocationRenamedEvent)

    def eventFilter(self, obj, event):
        if event and type(event) is LocationRenamedEvent:
            self.locationRenamed.emit(event)
            return True
        return QtCore.QObject.eventFilter(self, obj, event)

    @staticmethod
    def get_filter():
        if not hasattr(LocationRenamedEventFilter, "_filter"):
            core_app = QtCore.QCoreApplication.instance()
            _filter = LocationRenamedEventFilter(core_app)
            core_app.installEventFilter(_filter)
            LocationRenamedEventFilter._filter = _filter
        return LocationRenamedEventFilter._filter
