# btrdb_admin
# Package for the btrdb_admin database library.
#
# Author:   PingThings
# Created:  Mon Dec 17 15:23:25 2018 -0500
#
# For license information, see LICENSE.txt
# ID: __init__.py [] allen@pingthings.io $

"""
Package for the btrdb_admin database library.
"""

##########################################################################
## Imports
##########################################################################

import os
from btrdb_admin.conn import Connection
from btrdb_admin.exceptions import ConnectionError
from btrdb_admin.version import get_version
from btrdb_admin.utils import *


##########################################################################
## Module Variables
##########################################################################

__version__ = get_version()


##########################################################################
## Functions
##########################################################################


def connect(endpoint=None, username=None, password=None, profile=None):
    """
    Connect to a BTrDB server.

    Parameters
    ----------
    endpoint: str, default=None
        The address and port of the cluster to connect to, e.g. `192.168.1.1:4411`.
        If set to None will look up the string from the environment variable
        $BTRDB_ADMIN_ENDPOINTS (recommended).
    username: str, default=None
        Admin account username
    password: str, default=None
        Admin account password
    profile: str, default=None
        The name of a profile containing the required connection information as
        found in the user's predictive grid credentials file
        `~/.predictivegrid/credentials.yaml`.

    Returns
    -------
    db : BTrDB
        An instance of the BTrDB context to directly interact with the database.

    """
    if profile:
        return Connection(**credentials_by_profile(profile))

    creds = credentials(endpoint, username, password)

    if not creds.get("endpoint", False):
        raise ConnectionError("Connection string could not be determined.")

    if not creds.get("username", False) or not creds.get("password", False):
        raise ConnectionError("Username or password could not be determined.")

    return Connection(**creds)
