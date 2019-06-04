# ------- #
# Imports #
# ------- #

from difflib import Differ
from ..._vendor.simple_chalk import green, red, yellowBright
from .be import be
from .mixinRaise_ import mixinRaise_
from ...test import test
import os

from ...fns import (
    all_,
    contains,
    containsSubstring,
    isInstanceOf,
    joinWith,
    map_,
    passThrough,
)


# ---- #
# Init #
# ---- #

_d = Differ()
greenPlus = green("+")
isString = isInstanceOf(str)
redMinus = red("-")


# ---- #
# Main #
# ---- #


class to(mixinRaise_):
    def __init__(self, expectInst):
        self._expectInst = expectInst
        self._actual = self._expectInst._actual
        self.be = be(expectInst)

    @test
    def contain(self, expected):
        actual = self._actual

        if areStrings(actual, expected):
            return handleStringContain(actual, expected)

        elif contains(expected)(actual):
            return

        return f"expected {actual} to contain {expected}"

    @test
    def equal(self, expected):
        actual = self._actual

        if actual == expected:
            return

        if areStrings(actual, expected):
            return handleStringEqual(actual, expected)

        return f"expected {actual} to equal {expected}"

    @test
    def haveType(self, expected):
        expectInst = self._expectInst

        actualType = type(expectInst._actual)
        if actualType is expected:
            return

        actualName = actualType.__name__
        expectedName = expected.__name__
        return f"expected type '{expectedName}' but got '{actualName}'"


# ------- #
# Helpers #
# ------- #


def areStrings(*args):
    return all_(isString)(args)


def colorize(aLine):
    if aLine.startswith("+"):
        return greenPlus + aLine[1:]
    elif aLine.startswith("-"):
        return redMinus + aLine[1:]
    elif aLine.startswith("?"):
        return yellowBright(" " + aLine[1:])
    else:
        return aLine


def diff(left, right):
    result = _d.compare(left.splitlines(keepends=True), right.splitlines(keepends=True))
    return passThrough(result, [list, map_(colorize), joinWith("")])


def handleStringEqual(actual, expected):
    return (
        "the actual string is different than expected"
        + os.linesep
        + diff(actual, expected)
    )


def handleStringContain(actual, expected):
    if containsSubstring(actual)(expected):
        return

    return f"expected '{actual}' to contain '{expected}'"
