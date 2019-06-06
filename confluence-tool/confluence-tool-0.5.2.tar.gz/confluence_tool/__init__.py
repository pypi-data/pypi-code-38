"""
This module provides the main API of Confluence.  You can either import confluence_cli for having a confluence CLI or you import the API.
"""

try:
    from .confluence_api import ConfluenceError, ConfluenceAPI
    from .cli import command, arg, main
except ImportError:
    # this may happen in setup due to dependency issues
    pass

def argparse():
    return command.argparser

__version__ = "0.5.2"
