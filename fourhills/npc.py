import yaml
from dataclasses import dataclass
from typing import Optional, List, Dict
from fourhills.setting import Setting
from fourhills.stats import StatBlock
from fourhills.exceptions import (
    FourhillsFileLoadError, FourhillsSettingStructureError
)
from fourhills.text_utils import centre_pad, wrap_lines_paragraph


@dataclass
class Npc:
    """Represents a non-player character."""

    name: str
    appearance: str
    temperament: Optional[str] = None
    accent: Optional[str] = None
    phrases: Optional[List[str]] = None
    background: Optional[str] = None
    deceased: Optional[bool] = False
    stats: Optional[Dict] = None

    def __str__(self):
        return self.summary_info(line_width=80)

    def summary_info(self, line_width: int = 80) -> List[str]:
        """Return a list of lines summarising the NPC.

        Parameters
        ----------
        line_width : int
            The width of the output, in characters.

        Returns
        -------
        list of str
            A summary of the NPC block as a list of lines.
        """
        lines = []
        if self.deceased:
            lines.append(centre_pad(f"{self.name} (deceased)", line_width))
        else:
            lines.append(centre_pad(self.name, line_width))
        lines.append("=" * line_width)

        if self.stats:
            # Size, type and alignment
            lines.append(
                f"{self.stats.alignment.capitalize()} {self.stats.name} "
                f"({self.stats.size.capitalize()} {self.stats.creature_type})"
            )

        return wrap_lines_paragraph(lines, line_width)

    def battle_info(self, line_width: int = 80) -> List[str]:
        """Return a list of lines detailing the NPC's stats.

        Parameters
        ----------
        line_width : int
            The width of the output, in characters.

        Returns
        -------
        list of str
            A representation of the NPC's stats as a list of lines.
        """
        if self.stats:
            return self.stats.battle_info(line_width)
        else:
            return ["This NPC has no stats defined"]

    def character_info(self, line_width: int = 80) -> List[str]:
        """Return a list of lines describing the NPC.

        Parameters
        ----------
        line_width : int
            The width of the output, in characters.

        Returns
        -------
        list of str
            A representation of the NPC as a list of lines.
        """
        lines = []
        lines.append(f"Appearance: {self.appearance}")
        if self.accent:
            lines.append(f"Accent: {self.accent}")
        lines.append((self.temperament or "") + (" " + self.background or ""))

        if self.phrases:
            lines.append("")
            lines.append("Phrases:")
            for phrase in self.phrases:
                lines.append(f"- {phrase}")

        return wrap_lines_paragraph(lines, line_width)

    @classmethod
    def from_name(cls, name: str, setting: Setting):
        """Create an Npc by looking it up in the setting.

        Parameters
        ----------
        name: str
            The name of the NPC. Must exactly match a filename in the setting's
            `npcs` folder, excluding the extension.
        setting: Setting
            The Setting object; this is used to find the setting root and
            subdirectories.
        """
        # Suspected path of the NPC file
        npc_file = setting.npcs_dir / (name + ".yaml")
        if not npc_file.is_file():
            raise FourhillsSettingStructureError(f"NPC file {npc_file} does not exist.")
        with open(npc_file) as f:
            try:
                npc_dict = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise FourhillsFileLoadError(f"Error loading from {npc_file}.") from exc

            if "stats_base" in npc_dict:
                stats = StatBlock.from_name(npc_dict["stats_base"], setting)
            else:
                stats = None

            if "stats" in npc_dict:
                raise NotImplementedError

            npc = cls(
                **{
                    key: value
                    for key, value in npc_dict.items()
                    if key not in ["stats_base", "stats"]
                }
            )
            npc.stats = stats

            return npc
