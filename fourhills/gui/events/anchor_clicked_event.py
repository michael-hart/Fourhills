from PyQt5 import QtCore


class AnchorClickedEvent(QtCore.QEvent):

    EVENT_TYPE = None

    @staticmethod
    def registeredEventType():
        if AnchorClickedEvent.EVENT_TYPE is None:
            AnchorClickedEvent.EVENT_TYPE = QtCore.QEvent.registerEventType()
        return AnchorClickedEvent.EVENT_TYPE

    def __init__(self, url):
        super().__init__(AnchorClickedEvent.registeredEventType())
        self.url = url
