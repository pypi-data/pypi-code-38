from __future__ import print_function

from abc import ABCMeta

class HaloException(Exception):
    __metaclass__ = ABCMeta
    """
    The exception used when a template does not exist. Accepts the following
    optional arguments:


    """
    def __init__(self, msg, tried=None, backend=None, chain=None):
        super(HaloException, self).__init__(msg)


class HaloError(HaloException):
    __metaclass__ = ABCMeta
    """
    The exception used when a template does not exist. Accepts the following
    optional arguments:


    """
    def __init__(self, msg, tried=None, backend=None, chain=None):
        super(HaloError, self).__init__(msg)



class AuthException(HaloException):
    pass


class ApiException(HaloException):
    pass


class MaxTryException(ApiException):
    pass


class MaxTryHttpException(MaxTryException):
    pass


class MaxTryRpcException(MaxTryException):
    pass


class ApiTimeOutExpired(ApiException):
    pass


class ApiError(HaloError):
    pass


class DbError(HaloError):
    pass


class DbIdemError(DbError):
    pass


class CacheError(HaloError):
    pass


class CacheKeyError(CacheError):
    pass


class CacheExpireError(CacheError):
    pass

class BadRequestError(HaloError):
    __metaclass__ = ABCMeta
    """Custom exception class to be thrown when local error occurs."""
    def __init__(self, message, http_status=400, payload=None):
        self.message = message
        self.status = http_status
        self.payload = payload

class ProviderError(HaloError):
    pass