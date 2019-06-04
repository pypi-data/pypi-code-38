# ------- #
# Imports #
# ------- #

from .fns import discardFirst, passThrough
from .utils import getNumberOfLeadingSpaces


# ---- #
# Main #
# ---- #


def indentWith(anchor):
    def indentWith_inner(allLines):
        if anchor == 0:
            return allLines

        runningIndent = 0

        for i, oldLine in enumerate(allLines):
            allLines[i] = adjustWhitespace(allLines[i], anchor, runningIndent)
            runningIndent = passThrough(
                oldLine, [getNumberOfLeadingSpaces, updateIndent(runningIndent)]
            )

        return allLines

    def updateIndent(runningIndent):
        def updateIndent_inner(leadingSpaces):
            maybeNewIndent = leadingSpaces - anchor

            if maybeNewIndent == 0:
                return 0
            elif maybeNewIndent > 0:
                return maybeNewIndent
            else:
                return runningIndent

        return updateIndent_inner

    return indentWith_inner


# ------- #
# Helpers #
# ------- #


def adjustWhitespace(line, anchor, runningIndent):
    numberOfLeadingSpaces = getNumberOfLeadingSpaces(line)
    lineWithoutLeadingSpace = discardFirst(numberOfLeadingSpaces)(line)
    currentIndent = numberOfLeadingSpaces - anchor

    newLeadingSpace = 0

    if currentIndent > 0:
        newLeadingSpace = currentIndent
    elif currentIndent < 0:
        newLeadingSpace = numberOfLeadingSpaces + runningIndent

    return (" " * newLeadingSpace) + lineWithoutLeadingSpace
