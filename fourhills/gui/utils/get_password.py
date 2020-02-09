# from typing import Optional
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from fourhills.gui.utils.config import Config
from fourhills.utils.dnd_beyond_credentials import get_password, save_password


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cb_remember = QtWidgets.QCheckBox("Remember Me", self)
        self.cb_remember.setChecked(True)

        self.btn_check_creds = QtWidgets.QPushButton("Check Credentials", self)
        self.btn_check_creds.clicked.connect(self.check_creds)

        self.btn_use_user = QtWidgets.QPushButton("Set User Active", self)
        self.btn_use_user.clicked.connect(self.use_user)

        self.lbl_status = QtWidgets.QLabel(self)

        # So, we're actually going to have
        self.root_layout = QtWidgets.QHBoxLayout(self)

        new_form_layout = QtWidgets.QVBoxLayout()
        # new_form_layout.setAlignment(Qt.AlignVCenter)
        new_form_layout.addLayout(self.init_user())
        new_form_layout.addLayout(self.init_pass())
        cb_layout = QtWidgets.QHBoxLayout()
        cb_layout.setAlignment(Qt.AlignHCenter)
        cb_layout.addWidget(self.cb_remember)
        new_form_layout.addLayout(cb_layout)
        # new_form_layout.addWidget(self.cb_remember)
        new_form_layout.addWidget(self.btn_check_creds)
        new_form_layout.addWidget(self.lbl_status)

        # TODO status text (with spinner) for testing creds
        self.root_layout.addLayout(new_form_layout)

        existing_names = QtWidgets.QListWidget()
        existing_names.itemActivated.connect(self.on_item_activated)

        for name in Config.get_saved_users():
            existing_names.addItem(name)

        self.root_layout.addWidget(existing_names)

        self.txt_user.setFocus(True)

    def init_user(self):
        layout = QtWidgets.QHBoxLayout()
        self.lbl_user = QtWidgets.QLabel("Username:")
        self.txt_user = QtWidgets.QLineEdit(self)
        layout.addWidget(self.lbl_user)
        layout.addWidget(self.txt_user)
        return layout

    def init_pass(self):
        layout = QtWidgets.QHBoxLayout()
        self.lbl_pass = QtWidgets.QLabel("Password:")
        self.txt_pass = QtWidgets.QLineEdit(self)
        self.txt_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.lbl_pass)
        layout.addWidget(self.txt_pass)
        return layout

    def check_creds(self, event):
        user = self.txt_user.text()
        self.lbl_status.setText(f"Checking username: {user}")
        # TODO post to DnD Beyond and see if they're correct
        # TODO update a status text box with the result

    def use_user(self, _event):
        # Check username and password are non-empty
        user = self.txt_user.text()
        password = self.txt_pass.text()
        if not user or not password:
            QtWidgets.QErrorMessage.showMessage("Username or password is empty!")
            return

        # Set user as active, save password to system
        Config.set_active_user(user)
        save_password(user, password)

        # If user wants to be remembered, add to config
        if self.cb_remember.isChecked():
            Config.save_user(user)

    def on_item_activated(self, event):
        user = event.text()
        password = get_password(user)
        self.txt_user.setText(user)
        self.txt_pass.setText(password)


# def get_password() -> Optional[str]:
    # TODO get password from user
    # TODO offer usernames with saved passwords in storage if present

    # pass


if __name__ == "__main__":

    # Config.remove_user("test")
    # from fourhills.utils.dnd_beyond_credentials import clear_password
    # clear_password("test")

    # Config.save_user("test")

    # import sys
    # app = QtWidgets.QApplication(sys.argv)
    # login = LoginDialog()
    # login.show()
    # sys.exit(app.exec_())

    
