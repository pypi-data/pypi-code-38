
__copyright__ = "Copyright 2013-2014, http://radical.rutgers.edu"
__license__   = "MIT"


# ------------------------------------------------------------------------------
# we *first* import radical.utils, so that the monkeypatching of the logger has
# a chance to kick in before the logging module is pulled by any other 3rd party
# module, and also to monkeypatch `os.fork()` for the `atfork` functionality
import radical.utils as _ru
import os            as _os


# ------------------------------------------------------------------------------
# import NGE APIs
from nge_rp import NGE_RP
from nge_rs import NGE_RS


_mod_root = _os.path.dirname (__file__)

version_short, version_detail, version_base, \
               version_branch, sdist_name,   \
               sdist_path = _ru.get_version(_mod_root)
version = version_short

# ------------------------------------------------------------------------------

