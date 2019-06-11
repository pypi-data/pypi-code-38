from typing import TypeVar, Generic

TS = TypeVar("TS")  # Success Type
TF = TypeVar("TF")  # Failure Type


class Result(Generic[TS, TF]):
    _is_success: bool = False

    def __init__(self, success: TS = None, failure: TF = None) -> None:
        self._value_success = success
        self._value_failure = failure
        self._assert_values()

    def _assert_values(self):
        if (self._value_success is not None) and (self._value_failure is not None):
            raise TypeError(
                "Result is a monad, it cannot be success or failure. "
                "Please model your result selecting only one."
            )
        elif self._value_success is not None:
            self._is_success = True

    def get_value(self):
        if self._is_success:
            return self._value_success
        else:
            return self._value_failure

    def is_success(self):
        return self._is_success

    def is_failure(self):
        return not self._is_success

    value = property(get_value)
    is_success = property(is_success)
    is_failure = property(is_failure)
