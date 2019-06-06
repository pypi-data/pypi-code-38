# encoding: utf-8
from __future__ import print_function, division, absolute_import


class DataPoolException(Exception):
    pass


class ConsistencyError(DataPoolException):
    pass


class FormatError(DataPoolException):
    pass


class InvalidOperationError(DataPoolException):
    pass


class InvalidScriptName(DataPoolException):
    pass


class InvalidLandingZone(DataPoolException):
    pass


class InvalidConfiguration(DataPoolException):
    pass


class DataPoolIOError(DataPoolException):
    pass


class FatalError(DataPoolException):
    pass


class Message(DataPoolException):
    def __init__(self, message):
        self.message = message
