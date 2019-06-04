# ------- #
# Imports #
# ------- #

from .fns import discardLastWhile, passThrough
import re


# ---- #
# Init #
# ---- #

onlyWhitespaceRe = re.compile(r"\s*$")


# ---- #
# Main #
# ---- #


def areOnlyWhitespace(aString):
    return isOnlyWhitespace(aString)


def getNumberOfLeadingSpaces(line):
    i = 0

    for c in line:
        if c != " ":
            break
        i += 1

    return i


def isOnlyWhitespace(aString):
    return onlyWhitespaceRe.match(aString) is not None


def removeFirstAndLast(aList):
    aList.pop(0)
    aList.pop()
    return aList


#
# - removes any tailing lines which only contain whitespace
# - last line with a non-whitespace character has tailing whitespace removed
#
def trimLastLines(lines):
    return passThrough(
        lines, [discardLastWhile(isOnlyWhitespace), trimTheLastLine]
    )


# ------- #
# Helpers #
# ------- #


def trimTheLastLine(allLines):
    allLines[-1] = allLines[-1].rstrip()
    return allLines
