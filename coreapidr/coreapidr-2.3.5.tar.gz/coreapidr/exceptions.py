# coding: utf-8
from __future__ import unicode_literals


class coreapidrException(Exception):
    """
    A base class for all `coreapidr` exceptions.
    """
    pass


class ParseError(coreapidrException):
    """
    Raised when an invalid Core API encoding is encountered.
    """
    pass


class NoCodecAvailable(coreapidrException):
    """
    Raised when there is no available codec that can handle the given media.
    """
    pass


class NetworkError(coreapidrException):
    """
    Raised when the transport layer fails to make a request or get a response.
    """
    pass


class LinkLookupError(coreapidrException):
    """
    Raised when `.action` fails to index a link in the document.
    """
    pass


class ParameterError(coreapidrException):
    """
    Raised when the parameters passed do not match the link fields.

    * A required field was not included.
    * An unknown field was included.
    * A field was passed an invalid type for the link location/encoding.
    """
    pass


class ErrorMessage(coreapidrException):
    """
    Raised when the transition returns an error message.
    """
    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, repr(self.error))

    def __str__(self):
        return str(self.error)
