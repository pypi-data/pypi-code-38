import functools


class Grid5000Error(Exception):
    def __init__(self, error_message="", response_code=None,
                 response_body=None):

        Exception.__init__(self, error_message)
        # Http status code
        self.response_code = response_code
        # Full http response
        self.response_body = response_body
        # Parsed error message from gitlab
        try:
            # if we receive str/bytes we try to convert to unicode/str to have
            # consistent message types (see #616)
            self.error_message = error_message.decode()
        except Exception:
            self.error_message = error_message

    def __str__(self):
        if self.response_code is not None:
            return "{0}: {1}".format(self.response_code, self.error_message)
        else:
            return "{0}".format(self.error_message)


class Grid5000AuthenticationError(Grid5000Error):
    pass


class RedirectError(Grid5000Error):
    pass


class Grid5000ParsingError(Grid5000Error):
    pass


class Grid5000ConnectionError(Grid5000Error):
    pass


class Grid5000OperationError(Grid5000Error):
    pass


class Grid5000HttpError(Grid5000Error):
    pass


class Grid5000ListError(Grid5000OperationError):
    pass


class Grid5000GetError(Grid5000OperationError):
    pass


class Grid5000CreateError(Grid5000OperationError):
    pass


class Grid5000DeleteError(Grid5000OperationError):
    pass


def on_http_error(error):
    """Manage Grid5000HttpError exceptions.

    This decorator function can be used to catch Grid5000HttpError exceptions
    raise specialized exceptions instead.

    Args:
        error(Exception): The exception type to raise -- must inherit from
            Grid5000Error
    """
    def wrap(f):
        @functools.wraps(f)
        def wrapped_f(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Grid5000HttpError as e:
                raise error(e.error_message, e.response_code, e.response_body)
        return wrapped_f
    return wrap
