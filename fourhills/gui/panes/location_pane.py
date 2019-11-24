"""Definition for location pane, giving details about the selected location"""

import jinja2
import markdown
from pathlib import Path
from PyQt5 import QtWidgets

from fourhills import Setting
from fourhills.dataclasses import Location
from fourhills.gui.events import ObjectDeletedEventFilter, ObjectRenamedEventFilter
from fourhills.gui.widgets import ImageViewerWidget, LinkingBrowser


class LocationPane(QtWidgets.QWidget):

    map_pixmap = None

    def __init__(self, rel_path: Path, setting: Setting, parent=None):
        super().__init__(parent)

        self.rel_path = rel_path
        self.setting = setting

        # Jinja template initialiation
        jinja_env = jinja2.Environment(
            loader=jinja2.PackageLoader('fourhills', package_path='gui/templates')
        )

        self.location_template = jinja_env.get_template("location_info.j2")

        # Create events for location renaming and deleting
        renameFilter = ObjectRenamedEventFilter.get_filter()
        renameFilter.objectRenamed.connect(self.on_location_renamed)
        deleteFilter = ObjectDeletedEventFilter.get_filter()
        deleteFilter.objectDeleted.connect(self.on_location_deleted)

        # Create error message for bad map path that user can stop showing
        self.invalid_map_path_error = QtWidgets.QErrorMessage(self)

        # Give self a VBoxLayout for components
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.create_location_widget(self.rel_path, self.setting, self))

    def create_location_widget(self, rel_path, setting, parent=None):
        self.tab_widget = QtWidgets.QTabWidget(parent)

        loc_path = Location.get_location_path(rel_path, setting)
        if not loc_path.is_file():
            QtWidgets.QErrorMessage(self).showMessage(
                "Cannot open location {}; there must be a location.yaml file present".format(rel_path)
            )
            return

        scene_path = Location.get_scene_path(rel_path, setting)
        if not scene_path.is_file():
            scene_path.touch()

        self.loc_widget = LinkingBrowser(loc_path, self.render_location, parent=parent)
        self.scene_widget = LinkingBrowser(scene_path, self.render_scene, parent=parent)
        self.map_widget = ImageViewerWidget(self)

        self.loc_tab = self.tab_widget.addTab(self.loc_widget, "Location")
        self.scene_tab = self.tab_widget.addTab(self.scene_widget, "Description")
        self.map_tab = self.tab_widget.addTab(self.map_widget, "Map")

        self.update_map_tab()

        # Watch for file changes and add asterisks
        self.loc_widget.fileIsDifferent.connect(
            lambda: self.tab_widget.setTabText(self.loc_tab, "Location*")
        )
        self.loc_widget.fileIsSame.connect(
            lambda: self.tab_widget.setTabText(self.loc_tab, "Location")
        )
        self.scene_widget.fileIsDifferent.connect(
            lambda: self.tab_widget.setTabText(self.scene_tab, "Scene*")
        )
        self.scene_widget.fileIsSame.connect(
            lambda: self.tab_widget.setTabText(self.scene_tab, "Scene")
        )

        # Watch for loc_widget to save, then update the map
        self.loc_widget.fileSaved.connect(self.update_map_tab)

        return self.tab_widget

    def render_location(self, location_path):
        location = Location.from_name(location_path.parent, self.setting)
        return self.location_template.render(location=location)

    def render_scene(self, scene_path):
        if not scene_path.is_file():
            return ""
        with open(scene_path) as f:
            md_contents = f.read()
        return markdown.markdown(md_contents)

    @property
    def title(self):
        # Get last three parts of a location
        cut_path = Path(*self.rel_path.parts[-3:])
        return str(cut_path) + " (Location)"

    def on_location_renamed(self, event):
        if event.object_type != "Location" or self.rel_path != event.old_object:
            return

        self.rel_path = event.new_object
        loc_path = Location.get_location_path(self.rel_path, self.setting)
        scene_path = Location.get_scene_path(self.rel_path, self.setting)
        self.loc_widget.edit_path = loc_path
        self.scene_widget.edit_path = scene_path

        # Update window title
        self.parent().setWindowTitle(self.title)

    def on_location_deleted(self, event):
        if event.object_type == "Location" and self.rel_path == event.object_name:
            self.parent().close()

    def update_map_tab(self):
        # Check if location has map
        location = Location.from_name(self.rel_path, self.setting)
        if not location.map:
            self.tab_widget.setTabEnabled(self.map_tab, False)
            return

        # Check if map is valid file
        abs_path = Location.get_location_path(self.rel_path, self.setting).parent
        map_path = abs_path / location.map
        if not map_path.is_file():
            self.tab_widget.setTabEnabled(self.map_tab, False)
            self.invalid_map_path_error.showMessage(
                f"Cannot find file at given map path {map_path}"
            )
            return

        # Try to load and set to label
        self.map_widget.load_file(map_path)
        self.tab_widget.setTabEnabled(self.map_tab, True)
