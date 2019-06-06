""" useful things to import """

import pkg_resources

__version__ = str(pkg_resources.require("hilde")[0].version)

from ._defaults import (
    DEFAULT_CONFIG_FILE,
    DEFAULT_FIREWORKS_FILE,
    DEFAULT_GEOMETRY_FILE,
    DEFAULT_SETTINGS_FILE,
    supported_tasks,
)

from .settings import Settings, Configuration
from .templates.aims import setup_aims
from .helpers.restarts import restart
from .tasks import run
