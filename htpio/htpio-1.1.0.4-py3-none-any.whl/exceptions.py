# Copyright (c) Hilscher GmbH. All Rights Reserved.
#
# $Author: bgeorgiev $
# $Date: 2019-05-16 11:34:02 +0300 (Thu, 16 May 2019) $
# $Revision: 654 $

"""
This module implements all exception classes used by htpio.
"""

class PinLockedByOtherProcess(Exception):
    """ Raised when the gpio pin locked by another htpio process. """

    def __init__(self, lock_owner=None, my_session=None):
        self.lock_owner = lock_owner
        self.my_session = my_session

    def __str__(self):
        return repr(self.lock_owner + " (my session is " + self.my_session + ")")


class CannotCreateLockDirectory(Exception):
    """ Raised when the lockfolder cannot be created. """
    pass


class CannotMountRamDisk(Exception):
    """ Raised when the ram disk cannot be mapped to the lock folder. """
    pass


class InvalidLoginDetails(Exception):
    """ Raised when user or password provided not valid. """
    pass


class CannotConnectToTarget(Exception):
    """ Raised the object cannot connect to the specified [target:socket]. """
    pass
