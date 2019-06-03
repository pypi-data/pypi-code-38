class CQRSException(Exception):
    """Base exception for things that go wrong in commands and queries"""

    pass


class NotFound(CQRSException):
    """Raised when an item not found.

    This happens when trying to issue a command on a non-existent object
    or querying/retrieving a single non-existent object."""

    pass


class Forbidden(CQRSException):
    """Raised when the user doesn't have permission.

    This can be permission to query an object, or to execute a command."""

    pass


class Conflict(CQRSException):
    """Raised when a command's parameters conflict with current state.

    For instance, when trying to execute a command with a supposedly
    unique identifier that turns out not to be unique."""

    pass


class ConfigurationConflict(CQRSException):
    """Raised when there is a configuration conflict.

    For instance, when trying to retrieve infrastructure from the infrastructure
    factory but the infrastructure can't be initialized because the config is
    missing."""

    pass


class ValidationError(CQRSException):
    """Raised when command parameter validation fails.

    Will contain a list of detected errors."""

    pass
