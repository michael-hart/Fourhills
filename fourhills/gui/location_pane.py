"""Definition for location pane, giving details about the selected location"""

import jinja2
import markdown
from pathlib import Path
from PyQt5 import QtWidgets, QtCore

from fourhills import Location, Setting
from fourhills.gui.events import AnchorClickedEvent


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

        # Give self a VBoxLayout for components
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.location = Location.from_name(rel_path, setting)

        tab_widget = QtWidgets.QTabWidget(parent)
        loc_widget = self.create_loc_widget(self.location, tab_widget)
        scene_widget = self.create_scene_widget(self.location, tab_widget)
        tab_widget.addTab(loc_widget, "Location")
        if scene_widget:
            tab_widget.addTab(scene_widget, "Description")
        self.layout.addWidget(tab_widget)

    def create_loc_widget(self, location, parent=None):
        loc_edit = QtWidgets.QTextBrowser(parent)
        loc_edit.setHtml(self.location_template.render(location=location))
        loc_edit.setOpenLinks(False)
        loc_edit.setOpenExternalLinks(False)
        loc_edit.setReadOnly(True)
        loc_edit.anchorClicked.connect(self.post_anchor_clicked)
        return loc_edit

    def create_scene_widget(self, location, parent=None):
        scene_path = self.setting.world_dir / location.path / "scene.md"
        if not scene_path.is_file():
            return None
        with open(scene_path) as f:
            md_contents = f.read()
        md = markdown.markdown(md_contents)
        scene_edit = QtWidgets.QTextEdit(parent)
        scene_edit.setText(md)
        return scene_edit

    def post_anchor_clicked(self, event):
        QtCore.QCoreApplication.postEvent(
            QtCore.QCoreApplication.instance(),
            AnchorClickedEvent(event)
        )
