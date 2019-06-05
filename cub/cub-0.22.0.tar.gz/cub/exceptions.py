class CubException(Exception):
    """
    Parent for all Cub exceptions.
    """

    def __init__(self, msg=None, http_code=None, http_body=None,
                 json_body=None):
        super(CubException, self).__init__(msg)
        self.http_code = http_code
        self.http_body = http_body
        self.json_body = json_body


class ConnectionError(CubException):
    """
    Unable to connect to Cub API.
    """


class APIError(CubException):
    """
    There was a problem with Cub API.
    """


class Unauthorized(CubException):
    """
    You did not provide a valid API key.
    """


class BadRequest(CubException):
    """
    Some of request parameters passed to Cub were invalid.
    """


class Forbidden(CubException):
    """
    Access denied.
    """


class NotFound(CubException):
    """
    Requested object does not exist in Cub.
    """


class MethodNotAllowed(CubException):
    """
    Requested method is not allowed for this object.
    """


class InternalError(CubException):
    """
    Internal Cub error.
    """


class BadGateway(CubException):
    """
    Unexpected error occurred while communicating with target payment gateway.
    """


class ServiceUnavailable(CubException):
    """
    There was a problem while trying to fulfill your request.
    """
