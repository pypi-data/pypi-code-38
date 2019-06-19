from urllib3.exceptions import HTTPError

def status_error_handle(result):
    if 401 == result.status:
        exception = UnauthorizedException(401, "Unauthorized request")
        exception.response = result
        raise exception
    if 400 <= result.status < 500:
        exception = BadRequestException(result.status, "Bad Request")
        exception.response = result
        raise exception
    if result.status >= 500:
        exception = ServerException(result.status, "Server Exception")
        exception.response = result
        raise exception


class HTTPRequestException(HTTPError):
    """HTTP Exception"""

    def __init__(self, code, message):
        self.code = code
        self.message = message
        self.response = None


class UnauthorizedException(HTTPRequestException):
    """Unauthorized exception: 401 error"""
    pass


class BadRequestException(HTTPRequestException):
    """Bad request from server: 4xx error"""
    pass


class ServerException(HTTPRequestException):
    """Exception from service: 5xx error"""
    pass


class ConnectionException(HTTPError):
    """Can not establish connection"""
    pass


class ResourceFieldNotFoundException(Exception):
    def __init__(self, resource, field):
        """
        Unknown field exception
        :type resource: services.resource.AbstractResource
        :param resource: Resource
        :param field: unknown field
        """
        self.message = "Resource(%s) does not support field(%s). Declared(%s)" % (
            type(resource), field, resource.fields)
