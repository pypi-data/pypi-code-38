from .motion_lib_error_type import MotionLibErrorType


class MotionLibException(Exception):

    @property
    def error_type(self) -> MotionLibErrorType:
        """
        Specific error returned by the native library.
        """
        return self._error_type

    @property
    def message(self) -> str:
        """
        Error message of the exception.
        """
        return self._message

    def __init__(self, error_type: int, message: str):
        self._message = message
        self._error_type = MotionLibErrorType(error_type)
        Exception.__init__(self, "{}: {}".format(self._error_type.name, self._message))
