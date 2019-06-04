# ------- #
# Imports #
# ------- #

from .getTypedResult import getTypedResult
from .makeGenericCallFn import makeGenericCallFn
from ..decorators.argIsCallable import argIsCallable


# ---- #
# Main #
# ---- #


@argIsCallable
def discardWhen(predicate):
    fnName = discardWhen.__name__
    shouldDiscard = makeGenericCallFn(predicate, 3, fnName)

    def discardWhen_inner(collection):
        typedDiscardWhen = getTypedResult(collection, typeToDiscardWhen, fnName)
        return typedDiscardWhen(shouldDiscard, collection)

    return discardWhen_inner


# ------- #
# Helpers #
# ------- #


def discardWhen_list(shouldDiscard, aList):
    result = []
    for idx, el in enumerate(aList):
        if not shouldDiscard(el, idx, aList):
            result.append(el)

    return result


def discardWhen_dict(shouldDiscard, aDict):
    result = {}
    for key, val in aDict.items():
        if shouldDiscard(val, key, aDict):
            result[key] = val

    return result


typeToDiscardWhen = {list: discardWhen_list, dict: discardWhen_dict}
