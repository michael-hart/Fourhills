from appdirs import user_data_dir
import datetime
from pathlib import Path
from typing import List, Optional
import yaml

from fourhills.fourhills import AUTHOR, PACKAGE


class Config:

    @staticmethod
    def get_config_file() -> Path:
        return Path(user_data_dir(PACKAGE, AUTHOR)) / "config.yaml"

    @staticmethod
    def load_config() -> dict:
        conf_path = Config.get_config_file()
        if not conf_path.is_file():
            conf_path.parent.mkdir(parents=True, exist_ok=True)
            conf_path.touch()
            return {}
        else:
            conf = {}
            with open(conf_path) as f:
                conf = yaml.safe_load(f)
            if conf is None:
                conf = {}
            return conf

    @staticmethod
    def save_config(conf: dict):
        conf_path = Config.get_config_file()
        if not conf_path.is_file():
            conf_path.parent.mkdir(parents=True)
            conf_path.touch()
        with open(conf_path, 'w') as f:
            yaml.safe_dump(conf, f)

    @staticmethod
    def _validate_list(conf, key):
        if key not in conf:
            conf[key] = []
        if not type(conf[key] == list):
            conf[key] = []

    @staticmethod
    def _validate_recent_worlds(conf):
        Config._validate_list(conf, "recent_worlds")

    @staticmethod
    def _validate_saved_users(conf):
        Config._validate_list(conf, "saved_users")

    @staticmethod
    def dt_to_str(dt):
        return dt.isoformat()

    @staticmethod
    def str_to_dt(s):
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")

    @staticmethod
    def add_recent_world(recent_world: Path):
        world_name = str(recent_world)
        conf = Config.load_config()
        Config._validate_recent_worlds(conf)

        # Check if world already exists
        for world in conf["recent_worlds"]:
            if world["name"] == world_name:
                world["last_accessed"] = Config.dt_to_str(datetime.datetime.now())
                Config.save_config(conf)
                return

        # World does not exist, so add it
        world_dict = {
            "name": world_name,
            "last_accessed": Config.dt_to_str(datetime.datetime.now())
        }
        conf["recent_worlds"] += [world_dict]
        Config.save_config(conf)

    @staticmethod
    def get_recent_worlds(n: int = 5) -> List[Path]:
        conf = Config.load_config()
        Config._validate_recent_worlds(conf)

        worlds = []
        for world in conf["recent_worlds"]:
            world_dict = {
                "name": world["name"],
                "last_accessed": Config.str_to_dt(world["last_accessed"])
            }
            worlds += [world_dict]

        # Sort worlds by access time
        sorted_worlds = sorted(worlds, key=lambda x: x["last_accessed"])
        sorted_worlds.reverse()
        filtered_worlds = sorted_worlds[:n]

        return [Path(world["name"]) for world in filtered_worlds]

    @staticmethod
    def remove_recent_world(recent_world: Path):
        conf = Config.load_config()
        Config._validate_recent_worlds(conf)
        world_name = str(recent_world)
        for world in conf["recent_worlds"]:
            if world["name"] == world_name:
                conf["recent_worlds"].remove(world)
                Config.save_config(conf)
                return

    @staticmethod
    def last_opened():
        conf = Config.load_config()
        if "last_opened" not in conf:
            return None
        else:
            return Path(conf["last_opened"])

    @staticmethod
    def set_last_opened(last_opened):
        conf = Config.load_config()
        conf["last_opened"] = str(last_opened)
        Config.save_config(conf)

    @staticmethod
    def get_saved_users() -> List[str]:
        conf = Config.load_config()
        Config._validate_saved_users(conf)
        return conf["saved_users"]

    @staticmethod
    def save_user(username):
        conf = Config.load_config()
        Config._validate_saved_users(conf)
        if username not in conf["saved_users"]:
            conf["saved_users"] += [username]
        Config.save_config(conf)

    @staticmethod
    def remove_user(username):
        conf = Config.load_config()
        Config._validate_saved_users(conf)
        if username in conf["saved_users"]:
            conf["saved_users"].remove(username)
        Config.save_config(conf)

    @staticmethod
    def get_active_user() -> Optional[str]:
        conf = Config.load_config()
        if "active_user" in conf and conf["active_user"]:
            return conf["active_user"]
        return None

    @staticmethod
    def set_active_user(username):
        conf = Config.load_config()
        conf["active_user"] = username
        Config.save_config(conf)

    @staticmethod
    def clear_active_user():
        conf = Config.load_config()
        conf.pop("active_user", None)
        Config.save_config(conf)
