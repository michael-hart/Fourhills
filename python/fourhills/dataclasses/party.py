from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict
import yaml

from fourhills.setting import Setting
from fourhills.exceptions import (
    FourhillsFileLoadError, FourhillsSettingStructureError
)


@dataclass
class Party:
    """Represents a party of players existing within the setting."""
    name: str
    players: List[str]
    quests: Optional[Dict[str, str]] = None
    notes: Optional[str] = None

    def __str__(self):
        return "{}: {}".format(
            self.name,
            ", ".join(self.players)
        )

    @classmethod
    def from_name(cls, name: str, setting: Setting) -> "Party":
        """
        Create a Party by looking it up in the setting.

        Parameters
        ----------
        name: str
            The name of the Party. Must exactly match a filename in the setting's
            `parties` folder, excluding the extension.
        setting: Setting
            The Setting object; this is used to find the setting root and
            subdirectories.
        """
        party_file = Party.absolute_path(name, setting)
        if not party_file.is_file():
            raise FourhillsSettingStructureError(f"Party file {party_file} does not exist.")
        with open(party_file) as f:
            try:
                party_dict = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise FourhillsFileLoadError(f"Error loading from {party_file}.") from exc

            try:
                party = cls(
                    **{
                        key: value
                        for key, value in party_dict.items()
                    }
                )
            except TypeError as te:
                raise FourhillsFileLoadError from te

            return party

    @staticmethod
    def absolute_path(name: str, setting: Setting) -> Path:
        return setting.parties_dir / (name + ".yaml")
