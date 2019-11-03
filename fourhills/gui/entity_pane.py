from PyQt5 import QtWidgets


class EntityPane(QtWidgets.QWidget):

    def __init__(self, entity_type, entity_file, parent=None):
        super().__init__(parent)

        self.entity_type = entity_type
        self.entity_file = entity_file

        # Give self a VBoxLayout for components
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Component will be a QTextEdit containing raw YAML
        self.text_edit = QtWidgets.QTextEdit(self)
        self.layout.addWidget(self.text_edit)

        # Load the contents of the YAML
        with open(entity_file, 'r') as entity:
            entity_text = entity.read()

        self.text_edit.setText(entity_text)
