"""Definition for location pane, giving details about the selected location"""

import jinja2
import markdown
from pathlib import Path
from PyQt5 import QtWidgets

from fourhills import Location, Setting
from fourhills.gui.events import LocationRenamedEventFilter, LocationDeletedEventFilter
from fourhills.gui.linking_browser import LinkingBrowser


class LocationPane(QtWidgets.QWidget):

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
        renameFilter = LocationRenamedEventFilter.get_filter()
        renameFilter.locationRenamed.connect(self.on_location_renamed)
        deleteFilter = LocationDeletedEventFilter.get_filter()
        deleteFilter.locationDeleted.connect(self.on_location_deleted)

        # Give self a VBoxLayout for components
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # self.location = Location.from_name(rel_path, setting)
        self.layout.addWidget(self.create_location_widget(self.rel_path, self.setting, self))

    def create_location_widget(self, rel_path, setting, parent=None):
        self.tab_widget = QtWidgets.QTabWidget(parent)

        loc_path = Location.get_location_path(rel_path, setting)
        scene_path = Location.get_scene_path(rel_path, setting)
        if not scene_path.is_file():
            scene_path.touch()

        self.loc_widget = LinkingBrowser(loc_path, self.render_location, parent=parent)
        self.scene_widget = LinkingBrowser(scene_path, self.render_scene, parent=parent)

        self.loc_tab = self.tab_widget.addTab(self.loc_widget, "Location")
        self.scene_tab = self.tab_widget.addTab(self.scene_widget, "Description")

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
        if self.rel_path == event.old_location_path:
            self.rel_path = event.new_location_path
            loc_path = Location.get_location_path(self.rel_path, self.setting)
            scene_path = Location.get_scene_path(self.rel_path, self.setting)
            self.loc_widget.edit_path = loc_path
            self.scene_widget.edit_path = scene_path

            # Update window title
            self.parent().setWindowTitle(self.title)

    def on_location_deleted(self, event):
        if self.rel_path == event.location_path:
            self.parent().close()
