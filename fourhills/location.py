from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml

from fourhills.exceptions import (
    FourhillsFileLoadError, FourhillsSettingStructureError
)
from fourhills.setting import Setting


@dataclass
class Location:
    """Represents a location in the world."""

    path: Path = None
    name: Optional[str] = None
    npcs: Optional[str] = None
    monsters: Optional[str] = None
    environment: Optional[str] = None
    danger_level: Optional[str] = None
    description: Optional[str] = None
    map: Optional[str] = None

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.name)

    @classmethod
    def from_name(cls, path: Path, setting: Setting):
        """Create a Location by looking it up in the setting.

        Parameters
        ----------
        path: str
            The relative path from the world directory to the location, where
            the location is the directory containing location.yaml
        setting: Setting
            The Setting object; this is used to find the setting root and
            subdirectories.
        """
        loc_file = setting.world_dir / path / "location.yaml"
        if not loc_file.is_file():
            raise FourhillsSettingStructureError(f"Location file {loc_file} does not exist.")
        with open(loc_file) as f:
            try:
                loc_dict = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise FourhillsFileLoadError(f"Error loading from {loc_file}.") from exc

        loc = cls(
            **{
                key: value
                for key, value in loc_dict.items()
            }
        )
        loc.path = path
        return loc
