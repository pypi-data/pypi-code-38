# encoding: utf-8

""" APIUtil. """

# Get module version
from ._metadata import __version__

# Import key items from module

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
