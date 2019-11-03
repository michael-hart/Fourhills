"""Define a Qt Widget for the Notes Pane"""

from PyQt5 import QtWidgets, QtCore

from fourhills.gui.tab_result import TabResult


class NotesPane(QtWidgets.QWidget):

    STATUS_RESET_INTERVAL = 2000  # ms

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(QtWidgets.QLabel("DM Notes:"))

        # Add file information
        self.file_layout = QtWidgets.QHBoxLayout()
        self.load_btn = QtWidgets.QPushButton("Load File")
        self.save_btn = QtWidgets.QPushButton("Save File")
        self.file_path = QtWidgets.QLineEdit()
        self.file_path.setReadOnly(True)
        self.file_layout.addWidget(self.load_btn)
        self.file_layout.addWidget(self.save_btn)
        self.file_layout.addWidget(self.file_path)
        self.layout.addLayout(self.file_layout)

        # Set up button callbacks
        self.load_btn.clicked.connect(self.load_notes)
        self.save_btn.clicked.connect(self.save_notes)

        # Add notes text box
        self.notes_text = QtWidgets.QTextEdit()
        self.layout.addWidget(self.notes_text)

        # Add status label to inform user of file save/load success
        self.status_lbl = QtWidgets.QLabel()
        self.status_lbl.setAlignment(QtCore.Qt.AlignRight)
        self.layout.addWidget(self.status_lbl)

        self.setLayout(self.layout)

        # Timer for resetting the status label to no text
        self.status_timer = QtCore.QTimer(self)
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.reset_status)

    def load_notes(self):
        """Loads file from selected path and stores it for future saves"""
        path = self.select_load_file()[0]
        if not path:
            self.set_status("User cancelled file load.")
            return

        self.file_path.setText(path)
        with open(path) as f:
            self.notes_text.setText(f.read())
        self.set_status(f"Loaded notes from file: {path}")

    def save_notes(self):
        """Saves file if path is valid, else selects new file"""
        if not self.file_path.text():
            path = self.select_save_file()[0]
            if not path:
                self.set_status("User cancelled file selection.")
                return
            self.file_path.setText(path)

        with open(self.file_path.text(), 'w') as f:
            f.write(self.notes_text.toPlainText())
        self.set_status(f"Saved file to {self.file_path.text()}")

    def select_load_file(self):
        """Presents user with file selection dialog for existing notes location"""
        # Returns tuple of (absolute file path, filter option)
        return QtWidgets.QFileDialog.getOpenFileName(self, caption="Select Load Location")

    def select_save_file(self):
        """Presents user with file selection dialog for notes save location"""
        # Returns tuple of (absolute file path, filter option)
        return QtWidgets.QFileDialog.getSaveFileName(self, caption="Select Save Location")

    def set_status(self, status):
        """Sets status label and a timer to clear the status label after an interval"""
        if self.status_timer.isActive():
            self.status_timer.stop()
        if status:
            self.status_timer.setInterval(self.STATUS_RESET_INTERVAL)
            self.status_lbl.setText(status)
            self.status_timer.start()
        else:
            self.status_lbl.setText("")

    def reset_status(self):
        self.status_lbl.setText("")

    def has_focus(self):
        """Alternative to hasFocus which checks widget children for focus"""
        return (
            self.load_btn.hasFocus() or
            self.save_btn.hasFocus() or
            self.file_path.hasFocus() or
            self.notes_text.hasFocus()
        )

    def handle_tab(self, reverse=False):
        if not self.notes_text.hasFocus():
            self.notes_text.setFocus()
            return TabResult.TabConsumed
        return TabResult.TabRemaining
