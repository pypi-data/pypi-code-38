#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT Exceptions
# Copyright (C) 2011  Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class ProfileUnknownError(Exception):
    pass


class ProfileNotInCacheError(Exception):
    pass


class ProfileNotSetError(Exception):
    """This error raises when no profile has been set (value @NONE@ is found, but it should have been replaced)"""


class ProfileConnected(Exception):
    """This error is raised when trying to delete a connected profile."""


class ProfileNotConnected(Exception):
    pass


class ProfileKeyUnknown(Exception):
    pass


class ClientTypeError(Exception):
    """This code is not allowed for this type of client (i.e. component or not)"""


class UnknownEntityError(Exception):
    pass


class UnknownGroupError(Exception):
    pass


class MissingModule(Exception):
    # Used to indicate when a plugin dependence is not found
    # it's nice to indicate when to find the dependence in argument string
    pass


class NotFound(Exception):
    pass


class ConfigError(Exception):
    pass


class DataError(Exception):
    pass


class ConflictError(Exception):
    pass


class TimeOutError(Exception):
    pass


class CancelError(Exception):
    pass


class InternalError(Exception):
    pass


class FeatureNotFound(
    Exception
):  # a disco feature/identity which is needed is not present
    pass


class BridgeInitError(Exception):
    pass


class BridgeExceptionNoService(Exception):
    pass


class DatabaseError(Exception):
    pass


class PasswordError(Exception):
    pass


class PermissionError(Exception):
    pass


class ParsingError(Exception):
    pass


# Something which need to be done is not available yet
class NotReady(Exception):
    pass


class InvalidCertificate(Exception):
    """A TLS certificate is not valid"""
    pass


class CommandException(RuntimeError):
    """An external command failed

    stdout and stderr will be attached to the Exception
    """

    def __init__(self, msg, stdout, stderr):
        super(CommandException, self).__init__(msg)
        self.stdout = stdout
        self.stderr = stderr
