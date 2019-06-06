class ClientError(Exception):
    def __init__(self, message, cause=None):
        super(ClientError, self).__init__(message)
        self.message = message
        self.cause = cause


class AuthorisationError(ClientError):
    """
    In case ouath2 token could not be fetched.
    """


class RequestError(ClientError):
    pass


class ConnectionError(RequestError):
    pass


class Timeout(RequestError):
    """
    Request times out.
    """


class TooManyRedirects(RequestError):
    """
    Too many redirects for a request.
    """


class ReferencesMismatchException(ClientError):
    """
    When updating a resource and reference param does not match reference inside provided resource.zx
    """


class NotMatchingVersion(ClientError):
    """
    In case update cannot be perform because entity version in server is different from expected by client.xclxcl
    """


class HttpError(RequestError):
    def __init__(self, message, status_code):
        super(HttpError, self).__init__(message)
        self.status_code = status_code
