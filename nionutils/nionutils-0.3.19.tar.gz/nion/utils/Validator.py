"""
Validator classes. Useful for bindings.
"""

# standard libraries
# none

# third party libraries
# none

# local libraries
# none


class IntegerRangeValidator:
    """Validate an integer to a specific range."""

    def __init__(self, mn: int=None, mx: int=None):
        self.__min = mn
        self.__max = mx

    def validate(self, value: int) -> int:
        if self.__min is not None:
            value = max(self.__min, value)
        if self.__max is not None:
            value = min(self.__max, value)
        return value
