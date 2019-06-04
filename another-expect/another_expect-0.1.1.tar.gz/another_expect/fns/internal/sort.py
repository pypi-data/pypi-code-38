# ------- #
# Imports #
# ------- #

from .getTypedResult import getTypedResult


# ---- #
# Main #
# ---- #


def sort(collection):
    typedSort = getTypedResult(collection, typeToSort, "sort")
    return typedSort(collection)


# ------- #
# Helpers #
# ------- #


def sort_viaSorted(something):
    return sorted(something)


typeToSort = {list: sort_viaSorted}
