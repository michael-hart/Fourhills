from PyQt5 import QtCore


class LocationRenamedEvent(QtCore.QEvent):

    EVENT_TYPE = None

    @staticmethod
    def registeredEventType():
        if LocationRenamedEvent.EVENT_TYPE is None:
            LocationRenamedEvent.EVENT_TYPE = QtCore.QEvent.registerEventType()
        return LocationRenamedEvent.EVENT_TYPE

    def __init__(self, old_location_path, new_location_path):
        super().__init__(LocationRenamedEvent.registeredEventType())
        self.old_location_path = old_location_path
        self.new_location_path = new_location_path
