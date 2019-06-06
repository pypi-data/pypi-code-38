#Copyright 2013-2016 PhishMe, Inc.  All rights reserved.
#
#This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
#including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
#disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
#consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
#this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
from __future__ import unicode_literals, absolute_import


class PhishMeException(Exception):
    """
    Basic exception thrown by PhishMe configuration errors
    """
    pass


class PmValidationError(Exception):
    """
    Exception intended for validating PhishMe Intelligence configuration
    """
    pass


class PmSyncError(Exception):
    """
    Intended for user issues syncing with API
    """
    pass


class PmConnectionError(Exception):
    """
    For API connection issues
    """
    pass


class PmAttributeError(Exception):
    """
    For attribute errors in user specified code
    """
    pass


class PmBadConnectionType(Exception):
    """
    Invalid connection type passed
    """
    pass


class PmFileError(Exception):
    """
    Specified file is inaccessible, likely because of permissions issues
    """
    pass


class PmSearchTermError(Exception):
    """
    A search term being specified is incorrect.
    """
    pass


class PmNotImplemented(NotImplementedError):
    """
    To show when a user is using the wrong class to create an object
    """
    pass

