# Base class
class HttpError(Exception):
    pass


# Bad Request
class HttpBadRequest(HttpError):
    pass


# Unauthorized
class HttpUnauthorized(HttpError):
    pass


# Forbidden
class HttpForbidden(HttpError):
    pass


# Not Found
class HttpNotFound(HttpError):
    pass


# Method not allowed
class HttpNotAllowed(HttpError):
    pass


class InvalidContext(Exception):
    pass


class InvalidRelation(Exception):
    pass


class ParameterError(HttpBadRequest):
    pass