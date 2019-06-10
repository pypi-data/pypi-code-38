# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import sys
import traceback

from .models.error_response import ErrorResponseException


class AzureMLRestClientException(Exception):
    """
    Base class for all azureml exceptions.
    Extends Exception, if trying to catch only azureml exceptions
    then catch this class.
    """

    def __init__(self, exception_message, inner_exception=None, **kwargs):
        Exception.__init__(self, exception_message, **kwargs)
        self._exception_message = exception_message
        self._inner_exception = inner_exception
        self._exc_info = sys.exc_info()

    @property
    def message(self):
        return self._exception_message

    @message.setter
    def message(self, value):
        self._exception_message = value

    @property
    def inner_exception(self):
        return self._inner_exception

    @inner_exception.setter
    def inner_exception(self, value):
        self._inner_exception = value

    def print_stacktrace(self):
        traceback.print_exception(*self._exc_info)


class ServiceException(AzureMLRestClientException, ErrorResponseException):
    """
    An exception related to failed service calls. Contains the status code and
    any details if available related to the exception.
    """
    def __init__(self, error_response_exception, **kwargs):
        # Extending ServiceException to preserve all of the attributes of ErrorResponseException
        for key, value in error_response_exception.__dict__.items():
            setattr(self, key, value)
        # Errors created in the networking layer won't populate error_response_exception.error.error
        has_error = hasattr(error_response_exception, "error") and hasattr(error_response_exception.error, "error")
        self.details = error_response_exception.error.error.details if has_error else []
        self.status_code = error_response_exception.response.status_code

        AzureMLRestClientException.__init__(self, error_response_exception.message, error_response_exception)

    def __repr__(self):
        details_message = ""
        for error_detail in self.details:
            details_message += "\t\t{}\n".format(error_detail.message)
        return "ServiceException:\n\tCode: {}\n\tMessage: {}\n\tDetails:\n{}\n\tInnerException{}".format(
            self.status_code,
            self.message,
            details_message,
            self.inner_exception.error)

    def __str__(self):
        return self.__repr__()
