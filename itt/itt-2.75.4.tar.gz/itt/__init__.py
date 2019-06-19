
import better_exceptions

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger

# Get module version
from ._metadata import __version__

# Import key items from module
getLogger(__name__).addHandler(NullHandler())
