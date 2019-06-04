# ------- #
# Imports #
# ------- #

from .makeGenericCallFn import makeGenericCallFn
from .getTypedResult import getTypedResult
from ..decorators.argIsCallable import argIsCallable


# ---- #
# Main #
# ---- #


@argIsCallable
def reduce(fn, initial):
    reducerFn = makeGenericCallFn(fn, 4, "reduce")

    def reduce_inner(collection):
        typedReduce = getTypedResult(collection, typeToReduce, "reduce")
        return typedReduce(reducerFn, initial, collection)

    return reduce_inner


# ------- #
# Helpers #
# ------- #


def reduce_list(reducerFn, initial, aList):
    result = initial
    for idx, el in enumerate(aList):
        result = reducerFn(result, el, idx, aList)

    return result


typeToReduce = {list: reduce_list}
