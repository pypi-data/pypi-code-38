# ------- #
# Imports #
# ------- #

from math import inf
from .getNumPositionalParams import getNumPositionalParams
from .raise_ import raise_


# ---- #
# Main #
# ---- #


def makeGenericCallFn(fn, maxParams, callerName):
    required, allowed = getNumPositionalParams(fn, callerName)

    if allowed is inf:
        allowed = maxParams

    if required > maxParams:
        raise_(
            ValueError,
            f"""
            {callerName} can only take functions with up to {maxParams}
            positional params.  The function '{fn.__name__}' requires {required}
            """,
        )

    return lambda *args, **kwargs: fn(*args[:allowed], **kwargs)
