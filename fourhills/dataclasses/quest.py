from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import yaml

from fourhills import Setting
from fourhills.exceptions import (
    FourhillsFileLoadError, FourhillsSettingStructureError
)


@dataclass
class Quest:
    """Represents a possible quest for the party."""

    path: Path = None
    name: Optional[str] = None
    requirements: Optional[List[str]] = None
    rewards: Optional[List[str]] = None
    description: Optional[str] = None
    giver: Optional[str] = None
    start_location: Optional[str] = None

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.path)

    @classmethod
    def from_name(cls, path: Path, setting: Setting):
        """Create a quest by looking it up in the setting.

        Parameters
        ----------
        path: str
            The relative path from the quests directory to the quest, where
            the quest is the directory containing quest.yaml
        setting: Setting
            The Setting object; this is used to find the setting root and
            subdirectories.
        """
        quest_file = Quest.get_quest_path(path, setting)
        if not quest_file.is_file():
            raise FourhillsSettingStructureError(f"Quest file {quest_file} does not exist.")
        with open(quest_file) as f:
            try:
                quest_dict = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise FourhillsFileLoadError(f"Error loading from {quest_file}.") from exc

        if quest_dict is None:
            quest_dict = {}

        quest = cls(
            **{
                key: value
                for key, value in quest_dict.items()
            }
        )
        quest.path = path
        return quest

    @staticmethod
    def get_quest_path(path: Path, setting: Setting):
        return setting.quest_dir / path / "quest.yaml"

    @staticmethod
    def get_description_path(path: Path, setting: Setting):
        return setting.quest_dir / path / "description.md"
