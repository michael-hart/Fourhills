from PyQt5 import QtCore
from fourhills.gui.events.anchor_clicked_event import AnchorClickedEvent


class AnchorClickedEventFilter(QtCore.QObject):

    FILTER = None
    anchorClicked = QtCore.pyqtSignal(AnchorClickedEvent)

    def eventFilter(self, obj, event):
        if event and type(event) is AnchorClickedEvent:
            self.anchorClicked.emit(event)
            return True
        return QtCore.QObject.eventFilter(self, obj, event)

    @staticmethod
    def get_filter():
        if not hasattr(AnchorClickedEventFilter, "_filter"):
            core_app = QtCore.QCoreApplication.instance()
            _filter = AnchorClickedEventFilter(core_app)
            core_app.installEventFilter(_filter)
            AnchorClickedEventFilter._filter = _filter
        return AnchorClickedEventFilter._filter
