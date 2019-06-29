"""
PyApp - SQLAlchemy Extension

This extension provides a factory method for connecting to a SQL RDBMS.

"""
from pyapp.versioning import get_installed_version

from .factory import *

__name__ = "PyApp SQLAlchemy Extension"
__version__ = get_installed_version("pyApp-SQLAlchemy", __file__)
__default_settings__ = ".default_settings"
__checks__ = ".checks"
