# ------- #
# Imports #
# ------- #

from math import inf
from .returnFirstArgument import returnFirstArgument as identity
from .getNumPositionalParams import getNumPositionalParams


# ---- #
# Main #
# ---- #


def makeCallFn(fn, callerName, *, modifyResult=identity):
    (_, allowed) = getNumPositionalParams(fn, callerName)

    if allowed is inf:
        return lambda *args, **kwargs: modifyResult(fn(*args, **kwargs))

    else:
        return lambda *args, **kwargs: modifyResult(
            fn(*args[:allowed], **kwargs)
        )
