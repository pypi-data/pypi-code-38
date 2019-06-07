'''
Init.
'''
name = "gcshelpers"

from .config import CONFIG, pkgload
from .logger import LOGGER

__all__ = ["config", "logger", "telemetry"]
