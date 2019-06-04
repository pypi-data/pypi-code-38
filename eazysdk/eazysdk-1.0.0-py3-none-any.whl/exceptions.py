"""
eazysdk.excepions
~~~~~~~~~~~~~~~~~

This module contains the set of EazySDK's exceptions
"""
from functools import wraps


class EazySDKException(IOError):
    """ There was an unknown error that occurred while handling your
    request.
    """
    def __init__(self, message, *args):
        self.message = message
        super(EazySDKException, self).__init__(message, *args)


class UnsupportedHTTPMethodError(EazySDKException):
    """ The requested HTTP method is not available to EazySDK.
    """


class SDKNotEnabledError(EazySDKException):
    """ The API key is not enabled.
    """


class ResourceNotFoundError(EazySDKException):
    """ The requested resource could not be found using the parameters.
    """


class InvalidParameterError(EazySDKException):
    """ One or more of the parameters provided are not valid.
    """


class EmptyRequiredParameterError(EazySDKException):
    """ One or more of the required parameters have not been passed into
    the call.
    """


class ParameterNotAllowedError(EazySDKException):
    """ One or more parameters are mutually exclusive
    """


class InvalidEnvironmentError(EazySDKException):
    """ The environment provided was somehow invalid
    """


class InvalidStartDateError(EazySDKException):
    """ The selected start date of the contract is somehow invalid.
    """


class InvalidPaymentDateError(EazySDKException):
    """ The selected payment date is somehow invalid.
    """


class RecordAlreadyExistsError(EazySDKException):
    """ The record trying to be created already exists.
    """


class InvalidSettingsConfiguration(EazySDKException):
    """ A settings is not correct
    """


def common_exceptions_decorator(funct):
    @wraps(funct)
    def wrapper(self, *args, **kwargs):
        func = str(funct(self, *args, **kwargs))
        if 'not supported' in func:
            raise UnsupportedHTTPMethodError(
                'This is a generic error. This error can be caused by'
                'several events, including\n'
                '- The incorrect HTTP method is being used. Ex. You cannot use'
                ' the GET method when attempting to cancel a Direct Debit\n'
                '- The correct HTTP method is being used, but a mandatory '
                'field has been missed'
            )
        elif 'API not enabled' in func or 'does not support' in func:
            raise SDKNotEnabledError(
                'This is a generic error. This can be caused by several '
                'events, including\n'
                '- The API key is not correct.\n'
                '- The API is correct, but the client is not API enabled\n'
                '- The client code is not correct\n'
                '- If performing a POST, this could mean the record you\'re'
                ' trying to post against does not exist.'
            )
        elif 'IIS 8.5 Detailed Error - 404.0 - Not Found' in func\
                or 'No HTTP resource was found' in func:
            raise ResourceNotFoundError(
                'The requested resource could not be found. This is a'
                ' generic error which could be caused by several events,'
                ' including\n'
                '- You are searching against a record that does not exist\n'
                '- You are missing a mandatory parameter in your API call\n'
                '- You are trying to send invalid data to'
                ' EazyCustomerManager.\n'
                '- The provided client code or API key is incorrect.'
            )
        else:
            return func
    return wrapper
