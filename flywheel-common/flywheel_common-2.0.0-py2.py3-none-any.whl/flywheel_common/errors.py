"""Provide custom errors with additional detail"""

class ErrorBase(Exception):
    """Base Exception for common errors"""

    default_message = 'Unspecified error'

    def __init__(self, msg=None):
        self._msg = msg or self.default_message

    def __str__(self):
        return self._msg.format(**self.__dict__)


class ResourceError(ErrorBase):
    """Base class for errors that refer to a specific resource"""

    default_message = 'Resource error on "{path}"'

    def __init__(self, path, msg=None, exc=None):
        super(ResourceError, self).__init__(msg)
        self.path = path
        self.exc = exc


class ValidationError(ErrorBase):
    """Indicates that a user supplied invalid data"""

    default_message = 'Validation error, "{details}"'

    def __init__(self, msg=None, exc=None):
        super(ValidationError, self).__init__(msg)
        self.exc = exc
        self.details = '' if exc is None else str(exc)


class ResourceNotFound(ResourceError):
    """Indicates that a resource or file could not be found"""

    default_message = 'Could not find resource "{path}"'


class PermissionError(ResourceError):
    """Indicates that caller has insufficient permissions for this resource"""

    default_message = 'Insufficient permissions for "{path}"'


class OperationFailed(ErrorBase):
    """Indicates that an operation failed"""

    default_message = 'Operation failed, {details}'

    def __init__(self, msg=None, exc=None):
        super(OperationFailed, self).__init__(msg)
        self.exc = exc
        self.details = '' if exc is None else str(exc)


class RemoteConnectionError(OperationFailed):
    """Indicates that a connection error occurred."""

    default_message = 'Remote connection error, {details}'

class HTTPStatusError(ErrorBase):
    """Indicates that an HTTP request failed"""
    default_message = '{status_code} {reason}\n  detail: {detail}'

    def __init__(self, status_code, reason, detail=None):
        super(HTTPStatusError, self).__init__()

        self.status_code = status_code
        self.reason = reason
        self.detail = detail

    @staticmethod
    def raise_for_status(response):
        """Raise an HTTPStatusError if the given response object was not a 2xx or 3xx response.

        This method will check a requests.Response object (or any object with the same interface)
        if the response was `ok`, and raise a detailed error if not. If the response body is JSON
        and contains a `message` attribute, that will be used to populate the detail field on this message.

        Args:
            response (requests.Response): The response object to check.

        Raises:
            HTTPStatusError: If response.ok is False
        """
        if not response or response.ok:
            return

        try:
            detail = response.json().get('message')
        except:
            detail = None

        raise HTTPStatusError(response.status_code, response.reason, detail)
