# ------- #
# Imports #
# ------- #

from .internal.getTypedResult import getTypedResult


# ---- #
# Main #
# ---- #


def contains(separator):
    fnName = contains.__name__

    def contains_inner(collection):
        typedContains = getTypedResult(collection, typeToContains, fnName)
        return typedContains(separator, collection)

    return contains_inner


# ------- #
# Helpers #
# ------- #


def contains_list(elToCheck, aList):
    for el in aList:
        if el == elToCheck:
            return True

    return False


def contains_set(el, aSet):
    return el in aSet


typeToContains = {list: contains_list, set: contains_set}
