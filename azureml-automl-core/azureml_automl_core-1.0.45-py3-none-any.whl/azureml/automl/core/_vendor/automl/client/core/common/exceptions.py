# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exceptions thrown by AutoML."""
from typing import cast, Optional, Type, TypeVar


ExceptionT = TypeVar('ExceptionT', bound=BaseException)


class ErrorTypes:
    """Possible types of errors."""

    User = 'User'
    Service = 'Service'
    Client = 'Client'
    Resource = 'Resource'
    Unclassified = 'Unclassified'
    All = {User, Service, Client, Resource, Unclassified}


class AutoMLException(Exception):
    """Exception with an additional field specifying what type of error it is."""

    def __init__(self, message="", error_type=ErrorTypes.Unclassified):
        """
        Construct a new AutoMLException.

        :param error_type: type of the exception.
        :param message: details on the exception.
        """
        super().__init__(message)
        self.error_type = error_type

    @classmethod
    def from_exception(cls: 'Type[ExceptionT]', e: BaseException, msg: Optional[str] = None) -> ExceptionT:
        """Convert an arbitrary exception to this exception type."""
        if not msg and isinstance(e, cls):
            return cast(ExceptionT, e)
        return cast(ExceptionT, cls(msg or str(e)).with_traceback(e.__traceback__))


class DataException(AutoMLException):
    """
    Exception related to data validations.

    :param message: Details on the exception.
    """

    def __init__(self, message=""):
        """
        Construct a new DataException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.User)


class ConfigException(AutoMLException):
    """
    Exception related to invalid user config.

    :param message: Details on the exception.
    """

    def __init__(self, message=""):
        """
        Construct a new ConfigException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.User)


class ServiceException(AutoMLException):
    """
    Exception related to JOS.

    :param message: Details on the exception.
    """

    def __init__(self, message=""):
        """
        Construct a new ServiceException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.Service)


class ClientException(AutoMLException):
    """
    Exception related to client.

    :param message: Details on the exception.
    """

    def __init__(self, message=""):
        """
        Construct a new ClientException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.Client)


class ResourceException(AutoMLException):
    """
    Exception related to resource usage.

    :param message: Details on the exception.
    """

    def __init__(self, message=""):
        """
        Construct a new ResourceException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.Resource)


class OnnxConvertException(ClientException):
    """Exception related to ONNX convert."""


class DataprepException(ClientException):
    """Exceptions related to Dataprep."""
