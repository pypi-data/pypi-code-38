"""Exceptions thrown by limit function call implementations.

Adapted from https://github.com/sfalkner/pynisher
"""
from .constants import ClientErrors
from .exceptions import ClientException, ResourceException


class CpuTimeoutException(ResourceException):
    """Exception to raise when the cpu time exceeded."""

    def __init__(self):
        """Constructor."""
        super().__init__(ClientErrors.EXCEEDED_TIME_CPU)


class TimeoutException(ResourceException):
    """Exception to raise when the total execution time exceeded."""

    def __init__(self, value=None):
        """Constructor.

        :param value: time consumed
        """
        super().__init__(ClientErrors.EXCEEDED_TIME)
        self.value = value


class MemorylimitException(ResourceException):
    """Exception to raise when memory exceeded."""

    def __init__(self, value=None):
        """Constructor.

        :param value:  the memory consumed.
        """
        super().__init__(ClientErrors.EXCEEDED_MEMORY)
        self.value = value


class SubprocessException(ClientException):
    """Exception to raise when subprocess terminated."""

    def __init__(self, message=None):
        """Constructor.

        :param message:  Exception message.
        """
        if message is None:
            super().__init__(ClientErrors.SUBPROCESS_ERROR)
        else:
            super(SubprocessException, self).__init__(message)
