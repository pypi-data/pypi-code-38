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
def all_(predicate):
    fnName = all.__name__
    callPredicate = makeGenericCallFn(predicate, 3, fnName)

    def all_inner(collection):
        typedAll = getTypedResult(collection, typeToAll, fnName)
        return typedAll(callPredicate, collection)

    return all_inner


# ------- #
# Helpers #
# ------- #


def all_enumerable(callPredicate, enumerable):
    for idx, el in enumerate(enumerable):
        if not callPredicate(el, idx, enumerable):
            return False

    return True


def all_simpleNamespace(callPredicate, aSimpleNamespace):
    for key, val in aSimpleNamespace.__dict__.items():
        if not callPredicate(val, key, aSimpleNamespace):
            return False

    return True


typeToAll = {
    list: all_enumerable,
    SimpleNamespace: all_simpleNamespace,
    tuple: all_enumerable,
}
