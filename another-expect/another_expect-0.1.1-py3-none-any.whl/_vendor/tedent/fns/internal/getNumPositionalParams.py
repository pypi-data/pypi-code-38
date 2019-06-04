# ------- #
# Imports #
# ------- #

from inspect import Parameter
from math import inf
from .getFnSignature import getFnSignature
from .iif import iif


# ---- #
# Init #
# ---- #

_nonVarPositionalParamKinds = {
    Parameter.POSITIONAL_ONLY,
    Parameter.POSITIONAL_OR_KEYWORD,
}


# ---- #
# Main #
# ---- #

#
# Returns a tuple
#   numRequired: number of required positional params
#   numAllowed:  number of allowed positional params
#


def getNumPositionalParams(fn, callerName):
    sig = getFnSignature(fn, callerName)

    numAllowed = iif(_hasVarPositionalParam(sig), inf, 0)
    numRequired = 0

    for p in sig.parameters.values():
        if p.kind in _nonVarPositionalParamKinds:
            numAllowed += 1
            if p.default is Parameter.empty:
                numRequired += 1

    return (numRequired, numAllowed)


# ------- #
# Helpers #
# ------- #


def _hasVarPositionalParam(sig):
    for p in sig.parameters.values():
        if p.kind is Parameter.VAR_POSITIONAL:
            return True
