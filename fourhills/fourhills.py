import sys
import re
import yaml
import click
from typing import List, Tuple
from fourhills import Setting
from fourhills.dataclasses import StatBlock, Npc
from fourhills.exceptions import FourhillsFileLoadError
from fourhills.utils.text_utils import format_list, display_panes

SCENE_FILENAME = "battle.yaml"


class Scene:
    """Represents a particular location in the world."""

    def __init__(
        self, monster_names_quantities: List[Tuple[str, int]], npc_names: List[str]
    ):
        """Initialise the object."""
        self.monster_names_quantities = monster_names_quantities
        self.npc_names = npc_names
        self.setting = Setting()

    @classmethod
    def from_file(cls, filename: str):
        """Load scene info from a file and return a Scene instance.

        Parameters
        ----------
        filename : str
            Filename of the YAML file to load scene info from.
        """
        with open(filename) as f:
            try:
                scene_info = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise FourhillsFileLoadError(f"Error loading from {filename}.") from exc

            # Stores the list of monster names and numbers
            monster_info = []

            # If there was a monsters section, load the monsters
            if "monsters" in scene_info:
                for monster_name_number in scene_info["monsters"]:
                    # See if it matches the expected format, extracting name and number
                    match = re.match(r"^(\w*)(?: ?x?(\d+))?$", monster_name_number)
                    if not match:
                        raise FourhillsFileLoadError(
                            "Error parsing monster in scene file"
                        )
                    # Get the name of the monster and how many there are. If there
                    # wasn't a number, assume 1 monster.
                    name = match[1]
                    number = match[2] or "1"
                    # Convert to int
                    try:
                        number = int(number)
                    except ValueError as exc:
                        raise FourhillsFileLoadError(
                            f"Error parsing number for monster {name}"
                        ) from exc
                    # Add to the list
                    monster_info.append((name, number))

            # Stores the list of NPC names
            npc_info = scene_info["npcs"] if "npcs" in scene_info else []

            return cls(monster_info, npc_info)

    def display_battle(self):
        """Display statistsics for battle."""
        panes = list()

        for monster_name, quantity in self.monster_names_quantities:
            monster = StatBlock.from_name(monster_name, self.setting)
            panes.append(
                monster.summary_info(self.setting.pane_width, quantity)
                + monster.battle_info(self.setting.pane_width)
            )

        for npc_name in self.npc_names:
            npc = Npc.from_name(npc_name, self.setting)
            panes.append(
                npc.summary_info(self.setting.pane_width)
                + npc.battle_info(self.setting.pane_width)
            )

        display_panes(panes, self.setting.panes, self.setting.column_width)

    def display_npcs(self):
        """Display information about NPCs."""
        lines = list()

        for npc_name in self.npc_names:
            npc = Npc.from_name(npc_name, self.setting)
            lines.extend(npc.summary_info(self.setting.pane_width))
            lines.extend(npc.character_info(self.setting.pane_width))

        click.echo_via_pager("\n".join(lines))

    def display_scene(self):
        """Display information about location."""
        lines = list()
        monster_strings = [
            f"{name} x{quantity}" if quantity != 1 else name
            for name, quantity in self.monster_names_quantities
        ]
        lines.extend(format_list("Monsters", monster_strings, self.setting.pane_width))
        lines.extend(format_list("NPCs", self.npc_names, self.setting.pane_width))

        click.echo_via_pager("\n".join(lines))


def print_usage():
    raise NotImplementedError


def main():
    try:
        scene = Scene.from_file(SCENE_FILENAME)
    except FileNotFoundError:
        print("No scene file at this location")
        sys.exit()
    if len(sys.argv) > 1:
        if sys.argv[1] in ["b", "battle"]:
            scene.display_battle()
        elif sys.argv[1] in ["n", "npc", "npcs"]:
            scene.display_npcs()
        elif sys.argv[1] in ["s", "scene"]:
            scene.display_scene()
        else:
            print_usage()
    else:
        scene.display_scene()


if __name__ == "__main__":
    main()
