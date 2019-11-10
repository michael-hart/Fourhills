from PyQt5 import QtCore


class LocationDeletedEvent(QtCore.QEvent):

    EVENT_TYPE = None

    @staticmethod
    def registeredEventType():
        if LocationDeletedEvent.EVENT_TYPE is None:
            LocationDeletedEvent.EVENT_TYPE = QtCore.QEvent.registerEventType()
        return LocationDeletedEvent.EVENT_TYPE

    def __init__(self, location_path):
        super().__init__(LocationDeletedEvent.registeredEventType())
        self.location_path = location_path
