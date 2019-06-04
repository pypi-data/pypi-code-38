"""Exceptions raised by the Matchlight SDK."""
__all__ = (
    'APIError',
    'ConnectionError',
    'InvalidCredentialsError',
    'SDKError',
)


class SDKError(Exception):
    """Errors originating from within the Matchlight SDK."""


class APIError(SDKError):
    """Errors passed through from the Matchlight API."""


class ConnectionError(SDKError):
    """Custom error class for API request failures."""


class InvalidCredentialsError(ConnectionError):
    """Exception thrown when 401 Forbidden occurs."""
