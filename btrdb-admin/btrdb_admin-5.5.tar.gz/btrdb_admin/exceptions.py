# btrdb_admin.exceptions
# Module for custom exceptions
#
# Author:   PingThings
# Created:  Wed Mar 27 12:42:26 2019 -0400
#
# For license information, see LICENSE.txt
# ID: exceptions.py [] allen@pingthings.io $

"""
Module for custom exceptions
"""


class BTRDBError(Exception):
    pass

class ConnectionError(BTRDBError):
    """
    An error has occurred while interacting with the BTrDB server or when trying to establish a connection.
    """
    pass

class NotFoundError(BTRDBError):
    """
    An error has occurred while attempting to retrieve an item that does not exist
    """
    pass

class CredentialsFileNotFound(FileNotFoundError):
    """
    The credentials file could not be found.
    """
    pass

class ProfileNotFound(Exception):
    """
    A requested profile could not be found in the credentials file.
    """
    pass
