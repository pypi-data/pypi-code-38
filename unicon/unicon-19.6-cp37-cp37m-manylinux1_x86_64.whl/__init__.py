__version__ = '19.6'

import logging
log = logging.getLogger(__name__)

from unicon.eal.expect import Spawn
from unicon.core.pluginmanager import PluginManager
__plugin_manager__ = PluginManager()

# Unicon Connection Factory class
from unicon.bases.connection import Connection

__plugin_manager__.discover_builtin_plugins()
__plugin_manager__.discover_external_plugins()

# import the PyATS topology adapter
try:
    __import__('ats.topology')
except ImportError:
    # Do not complain, this may be a non PyATS setup
    pass
else:
    from unicon.adapters.topology import Unicon, XRUTConnect

# try to record usage statistics
#  - only internal cisco users will have stats.CesMonitor module
#  - below code does nothing for DevNet users -  we DO NOT track usage stats
#    for PyPI/public/customer users
try:
    # new internal cisco-only pkg since devnet release
    from ats.cisco.stats import CesMonitor
except Exception:
    try:
        # legacy pyats version, stats was inside utils module
        from ats.utils.stats import CesMonitor
    except Exception:
        CesMonitor = None

finally:
    if CesMonitor is not None:
        # CesMonitor exists -> this is an internal cisco user
        CesMonitor(action = __name__, application='pyATS Packages').post()
