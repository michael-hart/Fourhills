import jinja2
from pathlib import Path
import sys


def get_base_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parents[2]


def get_template_path() -> Path:
    """Returns the path to the template folder, accounting for app being frozen."""
    return get_base_path() / "templates"


def get_jinja_env() -> jinja2.Environment:
    """
    Returns environment that can retrieve render templates. The location that the templates are
    loaded from depends on whether the package has been frozen or not.
    """
    if getattr(sys, "frozen", False):
        current_path = get_base_path() / "render"
        loader = jinja2.FileSystemLoader(str(current_path))
    else:
        loader = jinja2.PackageLoader('fourhills', package_path='gui/templates')
    jinja_env = jinja2.Environment(loader=loader)
    return jinja_env
