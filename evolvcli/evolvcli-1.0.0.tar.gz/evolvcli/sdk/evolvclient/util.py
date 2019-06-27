import logging
import sys


log = logging.getLogger(sys.modules[__name__].__name__)


class EvolvError(Exception):
    """Generic Evolve exception class."""
    pass
