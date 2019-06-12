class AlreadyRegisteredError(Exception):
    """
    Raised when a resource has already been registered for the specified model.
    """


class ConfigurationError(Exception):
    """
    Raised when an issue is found that prevents the API from properly
    initialising.
    """


class UnsupportedMediaTypeError(Exception):
    """
    Raised when the API client sends an incorrect `Content-Type` header. The
    only supported header value is `application/vnd.api+json`.
    """


class NotAcceptableError(Exception):
    """
    Raised when the API client sends an incorrect `Accepts` header. The
    only supported header value is `application/vnd.api+json`.
    """


class MethodNotAllowedError(Exception):
    """
    Raised when the API client attempts to perform an operation on a resource
    that is not supported by that view, such as POSTing to a detail view.
    """


class BadRequestError(Exception):
    """
    Raised when JSON data can't be deserialised or other general parameter
    issues occur, like specifying a page number that isn't an integer.
    """


class UnprocessableEntityError(BadRequestError):
    """
    Raised when the JSON data is formatted correctly but a particular member
    of an object is invalid.
    """


class NotAuthenticatedError(Exception):
    """
    Raised when the API client attempts to perform an operation that requires
    authentication, but without having authenticated.
    """


class ForbiddenError(Exception):
    """
    Raised when the API client is authenticated successfully, but the operation
    being performed is not permitted by the authoriser.
    """


class ConflictError(Exception):
    """
    Raised when the API client attempts to save an object with an invalid ID
    or type member.
    """
