"""
OMXWare service Exception
"""
from omxware.exceptions.Error import Error
from enum import Enum


class ServiceException(Error):
    """Service Exception"""

    def __init__(self, message, status_code):
        super(ServiceException, self).__init__(message)

        self._original_code = status_code
        try:
            self._status_code = ServiceStatusCode(status_code)
        except ValueError:
            self._status_code = ServiceStatusCode.Unknown

    def get_status_code(self):
        """Return the status code"""
        return self._status_code

    def get_original_code(self):
        """Return the original code"""
        return self._original_code


class ServiceStatusCode(Enum):
    """ Service Status Code """
    Ok = 200
    Created = 201
    InvalidParameter = 400
    OperationNotPermitted = 403
    EntityNotFound = 404
    InternalError = 500
    Connect = 9000
    Unknown = 9999


class ServiceConnectionException(ServiceException):
    def __init__(self, message):
        super(ServiceConnectionException, self).__init__(message, ServiceStatusCode.Connect)
