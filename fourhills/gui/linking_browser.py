from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

from fourhills.exceptions import FourhillsError
from fourhills.gui.events import AnchorClickedEvent


class LinkingBrowser(QtWidgets.QTextBrowser):

    editing = False
    is_same = True
    _original_text = None

    fileIsSame = QtCore.pyqtSignal()
    fileIsDifferent = QtCore.pyqtSignal()

    def __init__(self, edit_path, render_html_fn, start_in_edit=False, editable=True, parent=None):
        super().__init__(parent)
        self._edit_path = edit_path
        self._render_html_fn = render_html_fn

        if start_in_edit:
            self.editing = True
            self.render_edit_from_file()
        else:
            try:
                self.render_view()
            except FourhillsError as fe:
                args = fe.args
                if not args:
                    args = fe.__cause__.args
                # Show user error message and set back to edit mode
                QtWidgets.QErrorMessage(self).showMessage(
                    "Cannot render file:\n" +
                    "\n".join(args)
                )
                self.edit()

        # Create keyboard shortcuts
        self.edit_action = QtWidgets.QAction("&Edit", self)
        self.save_action = QtWidgets.QAction("&Save", self)
        self.discard_action = QtWidgets.QAction("&Discard Changes", self)
        self.save_and_close_action = QtWidgets.QAction("Save and &Close", self)

        self.edit_action.setShortcut("Ctrl+E")
        self.save_action.setShortcut("Ctrl+S")
        self.discard_action.setShortcut("Ctrl+Q")
        self.save_and_close_action.setShortcut("Ctrl+Shift+S")

        self.edit_action.triggered.connect(self.edit)
        self.save_action.triggered.connect(self.save)
        self.discard_action.triggered.connect(self.discardChanges)
        self.save_and_close_action.triggered.connect(self.saveAndClose)

        self.addAction(self.edit_action)
        self.addAction(self.save_action)
        self.addAction(self.save_and_close_action)
        self.addAction(self.discard_action)

        # Allow user options for adding/renaming/deleting entities
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.editable = editable
        self.anchorClicked.connect(self.post_anchor_clicked)
        self.setOpenLinks(False)
        self.setOpenExternalLinks(False)

    def render_view(self):
        # Render the html using the function - allow exception to propagate to calling function
        html = self._render_html_fn(self._edit_path)
        self.setHtml(html)
        self.setReadOnly(True)

    def render_edit_from_file(self):
        # Read and display contents of edit file
        with open(self._edit_path) as ef:
            text = ef.read()
        self.render_edit_from_text(text)

    def render_edit_from_text(self, text):
        self._original_text = text
        self.setPlainText(text)
        self.setReadOnly(False)

    def show_context_menu(self, point_pos):
        # Get global position
        global_pos = self.mapToGlobal(point_pos)

        # Create menu and insert actions
        menu = QtWidgets.QMenu(self)
        if self.editing:
            menu.addAction(self.save_action)
            menu.addAction(self.save_and_close_action)
            menu.addAction(self.discard_action)
        else:
            menu.addAction(self.edit_action)

        # Show context menu at handling position
        menu.exec(global_pos)

    @property
    def edit_path(self):
        return self._edit_path

    @edit_path.setter
    def edit_path(self, edit_path):
        self._edit_path = edit_path

    @property
    def render_html_fn(self):
        return self._render_html_fn

    @render_html_fn.setter
    def render_html_fn(self, render_html_fn):
        self._render_html_fn = render_html_fn

    @property
    def editable(self):
        return self._editable

    @editable.setter
    def editable(self, editable):
        self.edit_action.setEnabled(editable)
        self.save_action.setEnabled(editable)
        self.save_and_close_action.setEnabled(editable)
        self.discard_action.setEnabled(editable)
        self._editable = editable

    @QtCore.pyqtSlot()
    def edit(self):
        if not self._editable or self.editing:
            return
        self.editing = True
        self.render_edit_from_file()

    @QtCore.pyqtSlot()
    def save(self):
        if not self.editing:
            return False
        # Get updated text and save to file
        text = self.toPlainText()
        with open(self._edit_path, 'w') as f:
            f.write(text)

        # Check file is valid
        try:
            self._render_html_fn(self._edit_path)
        except FourhillsError as fe:
            args = fe.args
            if not args:
                args = fe.__cause__.args
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot save file:\n" + "\n".join(args)
            )
            with open(self._edit_path, 'w') as f:
                f.write(self._original_text)
            return False

        # If file is valid, save updated original text
        self._original_text = text
        self.check_changes()

        return True

    @QtCore.pyqtSlot()
    def saveAndClose(self):
        # Save and close is just save followed by discard
        if self.save():
            self.discardChanges()

    @QtCore.pyqtSlot()
    def discardChanges(self):
        if not self.editing:
            return
        self.editing = False
        try:
            self.render_view()
        except FourhillsError as fe:
            args = fe.args
            if not args:
                args = fe.__cause__.args
            # Show user error message and set back to edit mode
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot render file:\n" +
                "\n".join(args)
            )
            self.edit()
            return
        self.check_changes()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.check_changes()

    def check_changes(self):
        if self.editing:
            text = self.toPlainText()
            if self.is_same:
                if text != self._original_text:
                    self.is_same = False
                    self.fileIsDifferent.emit()
                    print("Emitting file is different")
            else:
                if text == self._original_text:
                    self.is_same = True
                    self.fileIsSame.emit()
        else:
            if not self.is_same:
                self.is_same = True
                self.fileIsSame.emit()

    def post_anchor_clicked(self, event):
        QtCore.QCoreApplication.postEvent(
            QtCore.QCoreApplication.instance(),
            AnchorClickedEvent(event)
        )
