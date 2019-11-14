from pathlib import Path
from PyQt5 import QtWidgets


def make_path_dict(
        root_path: Path,
        path_filter: str,
        include_files: bool = True,
        include_file_endings: bool = False,
):
    items = {}
    for filter_file in root_path.rglob(path_filter):
        current_dict = items
        rel_path = filter_file.relative_to(root_path)

        if include_files:
            parts = rel_path.parts
        else:
            parts = rel_path.parent.parts

        for part in parts:
            if not part or part == ".":
                continue

            if include_file_endings:
                include_part = part
            else:
                include_part = str(Path(part).stem)

            if include_part not in current_dict:
                current_dict[include_part] = {}
            current_dict = current_dict[include_part]
    return items


def make_tree_from_items(items):
    tree_widget_items = []

    # Base case for recursive call is dictionary with no contents
    for key, val in items.items():
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, key)
        item.addChildren(make_tree_from_items(val))
        tree_widget_items += [item]

    return tree_widget_items


def make_tree_from_path(
        root_path: Path,
        path_filter: str,
        include_files: bool = True,
        include_file_endings: bool = False,
):
    items = make_path_dict(
        root_path,
        path_filter,
        include_files=include_files,
        include_file_endings=include_file_endings
    )
    return make_tree_from_items(items)
