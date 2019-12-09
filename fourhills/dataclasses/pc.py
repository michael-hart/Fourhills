from dataclasses import dataclass
from typing import Optional  # , List, Dict


@dataclass
class Npc:
    """Represents a player character."""

    name: str
    player_name: Optional[str] = None
    appearance: Optional[str] = None
    description: Optional[str] = None
    backstory: Optional[str] = None
