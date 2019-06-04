# ------- #
# Imports #
# ------- #

from .fns import all_, isEmpty, joinWith, passThrough, raise_
from .indentWith import indentWith
import os

from .utils import (
    areOnlyWhitespace,
    getNumberOfLeadingSpaces,
    isOnlyWhitespace,
    removeFirstAndLast,
    trimLastLines,
)

from .invalid import (
    invalidFewerThan3Lines,
    invalidFirstOrLastLine,
    invalidSecondLine,
)

# ---- #
# Main #
# ---- #


def tedent(aString):
    validateInput(aString)

    if isEmpty(aString):
        return ""

    allLines = aString.split(os.linesep)

    if len(allLines) < 3:
        if all_(areOnlyWhitespace)(allLines):
            return ""
        else:
            raise ValueError(invalidFewerThan3Lines)

    firstLine = allLines[0]
    secondLine = allLines[1]
    lastLine = allLines[-1]

    if not all_(areOnlyWhitespace)([firstLine, lastLine]):
        raise ValueError(invalidFirstOrLastLine)
    elif isOnlyWhitespace(secondLine):
        raise ValueError(invalidSecondLine)

    #
    # we got valid input fam
    #

    anchor = getNumberOfLeadingSpaces(secondLine)

    # allLines is being mutated for performance
    return passThrough(
        allLines,
        [removeFirstAndLast, indentWith(anchor), trimLastLines, joinWith("\n")],
    )


# ------- #
# Helpers #
# ------- #


def validateInput(input):
    if not isinstance(input, str):
        raise_(
            TypeError,
            f"""
            tedent requires a string

            type given: {type(input).__name__}
            """,
        )
