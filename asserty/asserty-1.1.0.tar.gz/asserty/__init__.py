"""asserty can be used to make assertions on object and works best in test contexts.

Import 'assert_that' (or 'that' if outside a context that handles AssertionError's) from asserty to make assertion.

Examples:
    >>> from asserty import that
    >>> assert that("Google".lower()).equals("google")

"""
from .asserts import Assert
from .expected_error import  expected_error

version = "1.1.0"
name = "asserty"


def assert_that(obj: object) -> Assert:
    """Make assertions on the given object.

    Args:
        obj (Any): The subject to which make assertions on.

    Returns:
        Assert: An class with assertion methods that work on the argument 'obj'
    """
    return Assert(obj)


that = assert_that
