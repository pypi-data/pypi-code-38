from http import HTTPStatus


class BadResponse(Exception):
    """
    Currently used if the response can't be json encoded, despite a .json extension
    """

    pass


class DeleteError(Exception):
    """
    Used when a delete request did not return a 200 or 204
    """

    pass


class HTTPException(Exception):
    def __init__(self, response, *args, **kwargs):
        try:
            message = response.json()["error"]
        except Exception:
            if hasattr(response, "status_code") and response.status_code == 401:
                message = response.json()
            else:
                message = response
        super(HTTPException, self).__init__(message, *args, **kwargs)


class HTTPBadRequest(HTTPException):
    """
    >= 400 Generic bad request error
    """

    pass


class HTTPUnauthorized(HTTPException):
    """
    401 Unauthorized
    Invalid API Key
    """

    pass


class HTTPForbidden(HTTPException):
    """
    403 Forbidden
    You do not have access to the requested resource
    """

    pass


class HTTPNotFound(HTTPException):
    """
    404 Not Found
    """

    pass


class HTTPUnprocessableEntity(HTTPException):
    """
    422 Unprocessable Entity
    One or more fields couldn't pass request validation
    """

    pass


class HTTPTooManyRequests(HTTPException):
    """
    429 Too Many Requests
    Rate limit exceeded,  you're sending too many requests!
    """

    pass


class HTTPInternalServerError(HTTPException):
    """
    500 Internal Server Error
    We had a problem with our server. Try again later.
    """

    pass


class HTTPServiceUnavailableError(HTTPException):
    """
    503 Service Unavailable
    We're temporarily offline for maintenance. Please try again later.
    """

    pass


class HTTPServerError(HTTPException):
    """
    >= 500 Generic server error
    """

    pass


def detect_and_raise_error(response):
    """
    Checks the response for errors and raises corresponding error.

    Raises:
        401 HTTPUnauthorized: Invalid API Key
        403 HTTPForbidden: You do not have access to the requested resource
        404 HTTPNotFound: Page not found
        422 HTTPUnprocessableEntity: One or more fields couldn't pass request validation
        409 HTTPTooManyRequests: Rate limit exceeded,  you're sending too many requests!
        500 HTTPInternalServerError: We had a problem with our server. Try again later.
        503 HTTPServiceUnavailableError: We're temporarily offline for maintenance. Please try again later.
        >=500 HTTPServerError: Generic server error
        >=400 HTTPBadRequest: Generic bad request error
    """
    if response.status_code == HTTPStatus.UNAUTHORIZED:  # 401
        raise HTTPUnauthorized(response)
    elif response.status_code == HTTPStatus.FORBIDDEN:  # 403
        raise HTTPForbidden(response)
    elif response.status_code == HTTPStatus.NOT_FOUND:  # 404
        raise HTTPNotFound(response)
    elif response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:  # 422
        raise HTTPUnprocessableEntity(response)
    elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:  # 429
        exc = HTTPTooManyRequests(response)
        exc.retry_after_secs = int(response.headers["Retry-After"])
        raise exc
    elif response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:  # 500
        raise HTTPInternalServerError(response)
    elif response.status_code == HTTPStatus.SERVICE_UNAVAILABLE:  # 503
        raise HTTPServiceUnavailableError(response)
    elif response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:  # >= 500
        raise HTTPServerError(response)
    elif response.status_code >= HTTPStatus.BAD_REQUEST:  # >= 400
        raise HTTPBadRequest(response)
