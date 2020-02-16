from cx_Freeze import setup, Executable

includefiles = [
    ("fourhills/gui/resources/icon.png", "resources/icon.png"),
    ("fourhills/templates", "templates"),
    ("fourhills/gui/templates", "render"),
]
includes = ["fourhills"]
excludes = ["tkinter"]
packages = ["os", "pkg_resources", "sys"]

setup(
    name="fourhills",
    version="0.0.1",
    description="A package for managing D&D campaigns",
    options={
        "build_exe": {
            "excludes": excludes,
            "packages": packages,
            "includes": includes,
            "include_files": includefiles
        }
    },
    executables=[Executable("fourhills/gui/main_window.py")]
)
