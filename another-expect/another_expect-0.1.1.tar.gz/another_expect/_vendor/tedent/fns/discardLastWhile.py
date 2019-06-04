# ------- #
# Imports #
# ------- #

from .decorators.argIsCallable import argIsCallable
from .internal.getTypedResult import getTypedResult
from .internal.makeGenericCallFn import makeGenericCallFn


# ---- #
# Main #
# ---- #


@argIsCallable
def discardLastWhile(predicate):
    fnName = discardLastWhile.__name__
    shouldDiscard = makeGenericCallFn(predicate, 3, fnName)

    def discardLastWhile_inner(collection):
        discardLastWhileFn = getTypedResult(
            collection, typeToDiscardLastWhile, fnName
        )
        return discardLastWhileFn(shouldDiscard, collection)

    return discardLastWhile_inner


# ------- #
# Helpers #
# ------- #


def discardLastWhile_viaSlice(shouldDiscard, sliceAble):
    i = len(sliceAble)
    for el in reversed(sliceAble):
        if not shouldDiscard(el, i, sliceAble):
            break

        i -= 1

    return sliceAble[:i]


typeToDiscardLastWhile = {
    list: discardLastWhile_viaSlice,
    str: discardLastWhile_viaSlice,
}
