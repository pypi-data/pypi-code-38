#
# README
#  - I'm not sure what to call this.  Its purpose is to centralize the type
#    validation, minimizing copy/paste.
#

# ------- #
# Imports #
# ------- #

from .raise_ import raise_
from .get import get


# ---- #
# Init #
# ---- #

getName = get("__name__")

#
# we need a unique object here to ensure the 'typeToSomething' doesn't lead us
#   to a 'None' value
#
nothing = object()


# ---- #
# Main #
# ---- #


def getTypedResult(value, typeToSomething, fnName):
    valueType = type(value)
    result = typeToSomething.get(valueType, nothing)

    if _isSomething(result):
        return result

    supportedTypes = ", ".join(map(getName, typeToSomething.keys()))
    raise_(
        ValueError,
        f"""\
        {fnName} doesn't support the type '{valueType.__name__}'
        supported types: {supportedTypes}
        """,
    )


# ------- #
# Helpers #
# ------- #


def _isSomething(x):
    return x is not nothing
