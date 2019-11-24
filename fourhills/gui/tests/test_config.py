import datetime
import os
from pathlib import Path
import pytest
import tempfile
import yaml

from fourhills.gui.utils import Config


@pytest.fixture
def clean_file():
    fd, tmp_path = tempfile.mkstemp()
    os.close(fd)
    yield tmp_path
    os.remove(tmp_path)


@pytest.fixture
def clean_config(clean_file):
    get_conf_fn = Config.get_config_file
    Config.get_config_file = lambda: Path(clean_file)
    yield
    Config.get_config_file = get_conf_fn


def test_config_path_is_yaml():
    p = Config.get_config_file()
    assert p.suffix == ".yaml"


def test_save_config(clean_config):
    conf = {"test": "test"}
    Config.save_config(conf)
    with open(Config.get_config_file()) as f:
        contents = yaml.safe_load(f)
    assert contents == conf


def test_validate_recent_worlds():
    conf = {}
    Config._validate_recent_worlds(conf)
    assert "recent_worlds" in conf


def test_dt_round_trip():
    now = datetime.datetime.now()
    assert Config.str_to_dt(Config.dt_to_str(now)) == now


def test_add_recent_world(clean_config):
    new_world = Path("test_world")
    Config.add_recent_world(new_world)
    with open(Config.get_config_file()) as f:
        contents = yaml.safe_load(f)

    assert len(contents["recent_worlds"]) == 1
    world = contents["recent_worlds"][0]
    assert world["name"] == new_world.name


def test_remove_recent_world(clean_config):
    new_world = Path("test_world")
    new_time = Config.dt_to_str(datetime.datetime.now())
    conf = {"recent_worlds": [{"name": str(new_world), "last_accessed": new_time}]}
    Config.save_config(conf)

    Config.remove_recent_world(new_world)

    with open(Config.get_config_file()) as f:
        contents = yaml.safe_load(f)

    assert len(contents["recent_worlds"]) == 0


def test_get_recent_worlds(clean_config):
    # Generate worlds
    conf = {"recent_worlds": []}
    world_names = []
    for idx in range(6):
        name = "world_{}".format(idx)
        time = datetime.datetime.now() - datetime.timedelta(minutes=idx)
        time_str = Config.dt_to_str(time)
        world = {"name": name, "last_accessed": time_str}
        conf["recent_worlds"] += [world]

        if idx < 5:
            world_names += [name]

    # Ensure config is not just returning first five files read
    conf["recent_worlds"].reverse()
    Config.save_config(conf)

    recent_worlds = Config.get_recent_worlds()
    assert len(recent_worlds) == 5
    for world in recent_worlds:
        assert str(world) in world_names
