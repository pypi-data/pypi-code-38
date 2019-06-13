"""Exports the expected_error class."""


class expected_error:
    """This class provides a context manager that wraps a given error.

    Example:
        >>> from asserty import expected_error
        >>> with expected_error(ValueError):
        ...     int("int")
        >>>
    """

    def __init__(self, err_type):
        if not isinstance(err_type, type):
            self.err_type = type(err_type)
        else:
            self.err_type = err_type

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        return isinstance(exception_value, self.err_type)
