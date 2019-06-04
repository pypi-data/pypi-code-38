# ------- #
# Imports #
# ------- #

from types import SimpleNamespace
from .internal.makeGenericCallFn import makeGenericCallFn
from .internal.getTypedResult import getTypedResult
from .decorators.argIsCallable import argIsCallable


# ---- #
# Main #
# ---- #


@argIsCallable
def forEach(fn):
    fnName = forEach.__name__
    callFn = makeGenericCallFn(fn, 3, fnName)

    def forEach_inner(collection):
        typedForEach = getTypedResult(collection, typeToForEach, fnName)
        return typedForEach(callFn, collection)

    return forEach_inner


# ------- #
# Helpers #
# ------- #


def forEach_dict(callFn, aDict):
    for key, val in aDict.items():
        callFn(val, key, aDict)

    return aDict


def forEach_list(callFn, aList):
    for idx, el in enumerate(aList):
        callFn(el, idx, aList)

    return aList


def forEach_simpleNamespace(callFn, aSimpleNamespace):
    forEach_dict(callFn, aSimpleNamespace.__dict__)
    return aSimpleNamespace


typeToForEach = {
    dict: forEach_dict,
    list: forEach_list,
    SimpleNamespace: forEach_simpleNamespace,
}
