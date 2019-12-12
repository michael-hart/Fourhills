from PyQt5 import QtWidgets
from PyQt5 import Qt, QtCore


class WorkspaceTabWidget(QtWidgets.QTabWidget):

    mdi_areas = []

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a tab containing the plus button
        self.tool_button = QtWidgets.QToolButton(self)
        self.tool_button.setText("+")
        self.tool_button.setAutoRaise(True)
        self.tool_button.clicked.connect(self.create_tab)

        # Plus symbols form part of the widget, we should have an empty
        # widget on the end to contain it
        self.addTab(QtWidgets.QWidget(), "")
        self.setTabEnabled(0, False)
        self.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, self.tool_button)

        # All other tab bar setup
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.tabCloseRequestedHandler)

        # Create initial tab
        self.create_tab(name="workspace")

        # Create rename actions for tabs
        self._context_menu = QtWidgets.QMenu()
        self._rename_action = QtWidgets.QAction("Rename Tab")
        self._rename_action.triggered.connect(self.rename_tab)
        self._context_menu.addAction(self._rename_action)
        self.tabBar().tabBarClicked.connect(self.tab_bar_clicked)

    def clear(self):
        # Remove leftmost tab until only + button remains
        while self.count() > 1:
            self.removeTab(0)
        self.mdi_areas = []
        self.create_tab(name="workspace")

    # Override insertTab and addTab to always keep + button on the right
    def addTab(self, widget, label):
        self.insertTab(self.count() - 1, widget, label)

    def insertTab(self, index, widget, label):
        index = min(self.count() - 1, index)
        index = max(0, index)
        super().insertTab(index, widget, label)

    # Remove tab on demand
    def tabCloseRequestedHandler(self, index):
        super().removeTab(index)

    def create_tab(self, checked: bool = False, name: str = None):
        if name is None:
            name, got_name = QtWidgets.QInputDialog.getText(
                self,
                "Enter new tab name",
                "Tab name:",
            )
            if not got_name:
                return

        self.mdi_areas += [QtWidgets.QMdiArea(self)]
        self.addTab(self.mdi_areas[-1], name)
        self.setCurrentIndex(self.count() - 2)

    def current_mdi_area(self):
        idx = self.currentIndex()
        if idx >= len(self.mdi_areas):
            return None
        return self.mdi_areas[idx]

    def tab_bar_clicked(self, tab_index):
        # Ignore the plus button tab
        if tab_index < 0:
            return
        # Ignore left clicks
        mouse_buttons = QtWidgets.QApplication.mouseButtons()
        if mouse_buttons != QtCore.Qt.RightButton:
            return
        self._last_tab_right_clicked = tab_index
        self._context_menu.popup(Qt.QCursor.pos())

    def rename_tab(self, event):
        name, got_name = QtWidgets.QInputDialog.getText(
            self,
            "Enter new tab name",
            "Tab name:",
        )
        if not got_name:
            return

        self.setTabText(self._last_tab_right_clicked, name)

    def customContextMenuRequested(self):
        print("Context menu requested")
