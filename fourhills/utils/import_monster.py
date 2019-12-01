import bs4
from pathlib import Path
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import yaml

from fourhills.exceptions import FourhillsMonsterImportError
from fourhills.utils.text_utils import slugify


def strip_inner(s):
    s_parts = re.split("\\s", s)
    s_word_parts = [word.strip() for word in s_parts if word.strip()]
    return " ".join(s_word_parts)


def escape(s):
    s = s.replace("\u2013", "-")
    s = s.replace("\u2019", "'")
    return s


def parse_melee(melee_desc):
    melee_regex = re.compile(
        "Melee Weapon Attack: (\\+\\d+) to hit, reach (\\d+ ft\\.), (.+)\\."
        " Hit: (.+? damage .*?)\\.(.*)"
    )
    match = melee_regex.match(melee_desc)
    melee_dict = {
        "hit": match.group(1),
        "reach": match.group(2),
        "targets": match.group(3),
        "damage": match.group(4),
    }
    if match.group(5):
        melee_dict["info"] = match.group(5).strip()
    return melee_dict


def parse_ranged(ranged_desc):
    ranged_regex = re.compile(
        "Ranged Weapon Attack: (\\+\\d+) to hit, range (.+ ft\\.), (.+)\\."
        " Hit: (.+? damage)\\.(.*)"
    )
    match = ranged_regex.match(ranged_desc)
    ranged_dict = {
        "hit": match.group(1),
        "range": match.group(2),
        "targets": match.group(3),
        "damage": match.group(4),
    }
    if match.group(5):
        ranged_dict["info"] = match.group(5).strip()
    return ranged_dict


def import_monster(monster_name: str, output_path: Path, monster_url=None):

    monster_slug = slugify(monster_name)

    if monster_url:
        url = monster_url
    else:
        url = "https://www.dndbeyond.com/monsters/" + monster_slug

    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    try:
        response = urlopen(req)
        content = response.read()
    except HTTPError as e:
        raise FourhillsMonsterImportError(f"No response from website for URL {url}") from e

    # Parse content using beautifulsoup
    soup = bs4.BeautifulSoup(content, 'html.parser')

    stat_blocks = soup.find_all("div", "mon-stat-block")
    if not stat_blocks:
        raise FourhillsMonsterImportError(f"Cannot access monster information at URL {url}.")

    stat_block = stat_blocks[0]

    # Parse out monster summary info
    name = stat_block.find_all("a", "mon-stat-block__name-link")[0].text.strip()
    meta = stat_block.find_all("div", "mon-stat-block__meta")[0]
    meta_parts = meta.text.strip().split(",")
    alignment = meta_parts[1].strip().capitalize()
    size = meta_parts[0].split(" ")[0]
    creature_type = " ".join(meta_parts[0].split(" ")[1:]).capitalize()

    ac = None
    hp = None
    speed = None

    for div in stat_block.find_all("div", "mon-stat-block__attribute"):
        label = div.find_all("span", "mon-stat-block__attribute-label")[0].text.strip()
        value_divs = div.find_all("span", "mon-stat-block__attribute-value")
        if value_divs:
            value = strip_inner(value_divs[0].text)
        data_divs = div.find_all("span", "mon-stat-block__attribute-data")
        if data_divs:
            data = strip_inner(data_divs[0].text)
        if label == "Armor Class":
            ac = value
        elif label == "Hit Points":
            hp = data
        elif label == "Speed":
            speed = data
        else:
            print("Unknown stat block attribute found during parse:", label)

    # Parse out stat block
    stats = [
        strip_inner(stat.text.strip()) for stat in
        stat_block.find_all("span", "ability-block__score")
    ]

    # Other skills
    skills = None
    senses = None
    languages = None
    challenge = None
    saving_throws = None
    damage_immunities = None
    condition_immunities = None
    damage_resistances = None
    damage_vulnerabilities = None
    for div in stat_block.find_all("div", "mon-stat-block__tidbit"):
        label = div.find_all("span", "mon-stat-block__tidbit-label")[0].text.strip()
        value = div.find_all("span", "mon-stat-block__tidbit-data")[0].text.strip()
        value_list = [strip_inner(val) for val in value.split(",")]
        if label == "Skills":
            skills = value_list
        elif label == "Senses":
            senses = value_list
        elif label == "Languages":
            languages = value_list
        elif label == "Challenge":
            challenge = ", ".join(value_list)
        elif label == "Damage Immunities":
            damage_immunities = value_list
        elif label == "Condition Immunities":
            condition_immunities = value_list
        elif label == "Saving Throws":
            saving_throws = value_list
        elif label == "Damage Resistances":
            damage_resistances = value_list
        elif label == "Damage Vulnerabilities":
            damage_vulnerabilities = value_list

    # Passive Perception is always the last sense
    passive_perception = int(senses[-1][len("Passive Perception "):])
    senses = senses[:-1]

    # Parse challenge fraction out
    if challenge:
        challenge = challenge.split(" ")[0]
        slash_split = challenge.split("/")
        # If challenge number has a rating, parse to decimal
        if len(slash_split) > 1:
            numerator = float(slash_split[0])
            denominator = float(slash_split[1])
            challenge = numerator / denominator
        else:
            challenge = float(challenge)

    # Parse out special traits, attacks, legendary actions
    special_traits = None
    actions = None
    legendary_actions = None

    description_blocks = stat_block.find_all("div", "mon-stat-block__description-block")
    for block in description_blocks:
        title = None
        headers = block.find_all("div", "mon-stat-block__description-block-heading")
        if headers:
            title = strip_inner(headers[0].text)

        # Form the dict from the actions
        block_dict = {}
        for p in block.find_all("p"):
            block_desc = p.text.strip()

            # Name is in bold, use -1 to strip . at the end
            strong_text = p.find_all("strong")
            if strong_text:
                block_name = p.find_all("strong")[0].text.strip()[:-1]
                # Remove the name of the attack from the beginning to get the description
                # Include the full stop and space after the title from removal
                block_desc = block_desc[len(block_name) + 2:]
            else:
                block_name = "Extra info"
            block_dict[block_name] = block_desc

        if title == "Actions":
            actions = block_dict
        elif title == "Legendary Actions":
            legendary_actions = block_dict
        else:
            special_traits = block_dict

    # Split actions into melee_attacks, ranged_attacks, and other_actions
    melee_attacks = {}
    ranged_attacks = {}
    other_actions = {}

    for action, desc in actions.items():
        action = escape(action)
        desc = escape(desc)
        if desc.startswith("Melee Weapon Attack"):
            melee_attacks[action] = parse_melee(desc)
        elif desc.startswith("Ranged Weapon Attack"):
            ranged_attacks[action] = parse_ranged(desc)
        else:
            other_actions[action] = desc

    # Parse out description, if present
    description = None
    description_blocks = soup.find_all("div", "mon-details__description-block-content")
    if description_blocks:
        description = strip_inner(description_blocks[0].text)

    # Parse out lair actions, if present
    lair_actions = None
    lair_blocks = description_blocks
    for lair_block in lair_blocks:
        lair_title = lair_block.find_all("p", string='Lair Actions')
        if lair_title:
            lair_actions = {}
            for element in lair_title[0].next_siblings:
                if type(element) == bs4.element.NavigableString:
                    continue
                lines = element.find_all("li")
                if lines:
                    actions = []
                    # Form the dict from the actions
                    for li in lines:
                        actions += [escape(strip_inner(li.text))]
                    lair_actions["actions"] = actions
                    # Break as ul always finishes the block of actions off
                    break

                element_text = escape(strip_inner(element.text))
                lair_actions["description"] = element_text

    # Put gathered information into a dictionary, dump to file, then attempt to read as stat block
    monster_info = {
        "name": name,
        "size": size,
        "creature_type": creature_type,
        "alignment": alignment,
        "ac": ac,
        "hp": hp,
        "speed": speed,
        "ability": {
            "STR": int(stats[0]),
            "DEX": int(stats[1]),
            "CON": int(stats[2]),
            "INT": int(stats[3]),
            "WIS": int(stats[4]),
            "CHA": int(stats[5]),
        },
        "passive_perception": passive_perception,
        "challenge": challenge,
    }

    if saving_throws:
        monster_info["saving_throws"] = {}
        for throw in saving_throws:
            stat, val = throw.split(" ")
            monster_info["saving_throws"][stat] = val

    if damage_immunities:
        parts = ", ".join(damage_immunities).split("; ")
        if len(parts) == 1:
            monster_info["damage_immunities"] = damage_immunities
        else:
            separated_immunities = []
            for part in parts:
                if "Nonmagical" in part:
                    separated_immunities += [part]
                else:
                    separated_immunities += part.split(", ")
            monster_info["damage_immunities"] = damage_immunities

    if skills:
        monster_info["skills"] = {}
        for skill in skills:
            stat, val = skill.split(" ")
            monster_info["skills"][stat] = val

    if condition_immunities:
        monster_info["condition_immunities"] = condition_immunities

    if damage_resistances:
        parts = ", ".join(damage_resistances).split("; ")
        if len(parts) == 1:
            monster_info["damage_resistances"] = damage_resistances
        else:
            separated_resistances = []
            for part in parts:
                if part.contains("Nonmagical"):
                    separated_resistances += [part]
                else:
                    separated_resistances += part.split(", ")
            monster_info["damage_resistances"] = damage_resistances

    if damage_vulnerabilities:
        parts = ", ".join(damage_vulnerabilities).split("; ")
        if len(parts) == 1:
            monster_info["damage_vulnerabilities"] = damage_vulnerabilities
        else:
            separated_vulnerabilities = []
            for part in parts:
                if part.contains("Nonmagical"):
                    separated_vulnerabilities += [part]
                else:
                    separated_vulnerabilities += part.split(", ")
            monster_info["damage_vulnerabilities"] = damage_vulnerabilities

    if senses:
        monster_info["special_senses"] = {}
        for sense in senses:
            sense_name = sense.split(" ")[0]
            sense_val = " ".join(sense.split(" ")[1:])
            monster_info["special_senses"][sense_name] = sense_val

    if languages:
        monster_info["languages"] = languages

    if special_traits:
        monster_info["special_traits"] = special_traits

    if melee_attacks:
        monster_info["melee_attacks"] = melee_attacks

    if ranged_attacks:
        monster_info["ranged_attacks"] = ranged_attacks

    if other_actions:
        monster_info["other_actions"] = other_actions

    if legendary_actions:
        monster_info["legendary_actions"] = legendary_actions

    if lair_actions:
        monster_info["lair_actions"] = lair_actions

    if description:
        monster_info["description"] = description

    # Dump to yaml file in output_path
    with open(output_path, 'w') as f:
        yaml.safe_dump(monster_info, f, sort_keys=False)
