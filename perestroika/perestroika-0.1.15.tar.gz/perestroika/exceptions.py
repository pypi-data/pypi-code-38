class RestException(Exception):
    def __init__(self, message=None, status_code=None, errors=None) -> None:
        self.message = message
        self.status_code = status_code
        self.errors = errors or []

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"


class BadRequest(RestException):
    def __init__(self, message=None, errors=None) -> None:
        super().__init__(message, 400, errors)


class InternalServerError(RestException):
    def __init__(self, message=None, errors=None) -> None:
        super().__init__(message, 500, errors)


class MethodNotAllowed(RestException):
    def __init__(self, message=None, errors=None) -> None:
        super().__init__(message, 405, errors)
