"""
This module provides the main API of Confluence.  You can either import confluence_cli for having a confluence CLI or you import the API.
"""

from .confluence_api import ConfluenceError, ConfluenceAPI
from .cli import command, arg, main

def argparse():
    return command.argparser

__version__ = "0.5.1"