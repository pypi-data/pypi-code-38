# ------- #
# Imports #
# ------- #

from ...fns import raise_ as raiseError
from ...test import test
from inspect import isclass


# ---- #
# Main #
# ---- #


class mixinRaise_:
    @test
    def raise_(self, expected):
        expectInst = self._expectInst

        if not callable(expectInst._actual):
            raiseError(
                ValueError,
                "in order to call 'raise_', the expected value must"
                " be callable",
            )

        raiseFn = _getRaiseFn(expected)
        if raiseFn is None:
            raiseError(
                ValueError,
                f"""\
                'raise' must be given a class or string

                value provided: {expected}
                """,
            )

        return raiseFn(expectInst, expected)


# ------- #
# Helpers #
# ------- #


def _raiseMatchingSubstring(expectInst, aSubString):
    try:
        expectInst._actual()

        return f"""\
            No exception was raised

            expected an exception to match: {aSubString}
            """
    except Exception as e:
        eStr = str(e)
        if aSubString not in eStr:
            return f"""\
                An exception was raised but no matching string was found

                expected to match: {aSubString}
                actual error string: {eStr}
                """


def _raiseInstanceOf(expectInst, aClass):
    try:
        expectInst._actual()
        return f"""\
            No exception was raised

            expected an exception to be an instance of {aClass.__name__}
            """
    except aClass:
        return
    except Exception as e:
        name = aClass.__name__
        return f"""\
            An exception was raised but it wasn't an instance of {name}

            actual error class name: {e.__class__.__name__}
            """


def _getRaiseFn(something):
    if type(something) is str:
        return _raiseMatchingSubstring
    elif isclass(something):
        return _raiseInstanceOf
