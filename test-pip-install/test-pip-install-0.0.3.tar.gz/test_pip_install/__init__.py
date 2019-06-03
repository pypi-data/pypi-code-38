"""Test if `pip install` is working"""

import sys


def info():
    """Print info on the current Python instance
    """
    version_info = sys.version_info
    version = "{0:}.{1:}.{2:}".format(*version_info[:3])
    if version_info[3] != "final":
        version += " ({0:}, {1:})".format(*version_info[3:])
    print("running Python {0:s} from {1:s}".format(version, sys.executable))
