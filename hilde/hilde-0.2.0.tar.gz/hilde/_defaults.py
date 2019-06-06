""" some default naming """

from pathlib import Path

supported_tasks = ["phonopy", "phono3py", "md"]

HOME = Path().home()

DEFAULT_CONFIG_FILE = HOME / '.hilderc'
DEFAULT_FIREWORKS_FILE = HOME / ".fireworksrc"
DEFAULT_GEOMETRY_FILE = "geometry.in"
DEFAULT_SETTINGS_FILE = "settings.in"
DEFAULT_TEMP_SETTINGS_FILE = "temp_settings.in"
