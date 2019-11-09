from PyQt5 import QtWidgets


class LocationTreePane(QtWidgets.QDockWidget):

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.location_tree = QtWidgets.QTreeWidget(self)
        # self.location_tree.setColumnCount(1)
        self.setWidget(self.location_tree)

    def load(self, path):
        """Search path for YAML files and load them as locations"""
        self.location_tree.clear()

        if not path.is_dir():
            # Path does not exist, ignore
            return

        items = {}
        for location_file in path.rglob("location.yaml"):
            current_dict = items
            rel_path = location_file.relative_to(path)

            for part in rel_path.parent.parts:
                if not part or part == ".":
                    continue
                if part not in current_dict:
                    current_dict[part] = {}
                current_dict = current_dict[part]

        # Recursively create sub levels of tree and add to tree control
        top_level = self.create_tree_widget_items(items)
        self.location_tree.addTopLevelItems(top_level)

    def create_tree_widget_items(self, items):
        tree_widget_items = []

        # Base case for recursive call is dictionary with no contents
        for key, val in items.items():
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, key)
            item.addChildren(self.create_tree_widget_items(val))
            tree_widget_items += [item]

        return tree_widget_items
