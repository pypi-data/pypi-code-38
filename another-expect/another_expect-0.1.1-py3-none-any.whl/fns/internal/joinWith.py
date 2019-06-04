# ------- #
# Imports #
# ------- #

from ..._vendor.ordered_set import OrderedSet
from .getTypedResult import getTypedResult


# ---- #
# Main #
# ---- #


def joinWith(separator):
    def joinWith_inner(collection):
        typedJoinWith = getTypedResult(collection, typeToJoinWith, "joinWith")
        return typedJoinWith(separator, collection)

    return joinWith_inner


# ------- #
# Helpers #
# ------- #


def joinWith_iterable(separator, aList):
    return separator.join(aList)


typeToJoinWith = {list: joinWith_iterable, OrderedSet: joinWith_iterable}
