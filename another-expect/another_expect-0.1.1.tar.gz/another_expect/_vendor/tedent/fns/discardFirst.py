# ------- #
# Imports #
# ------- #

from .internal.getTypedResult import getTypedResult


# ---- #
# Main #
# ---- #


def discardFirst(n):
    fnName = discardFirst.__name__

    def discardFirst_inner(collection):
        discardFn = getTypedResult(collection, typeToDiscardFirst, fnName)
        return discardFn(n, collection)

    return discardFirst_inner


# ------- #
# Helpers #
# ------- #


def discardFirst_viaSlice(n, sliceAble):
    return sliceAble[n:]


typeToDiscardFirst = {list: discardFirst_viaSlice, str: discardFirst_viaSlice}
