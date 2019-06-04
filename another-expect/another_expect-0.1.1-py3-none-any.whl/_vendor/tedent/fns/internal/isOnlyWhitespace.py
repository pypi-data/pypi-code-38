import re

onlyWhitespaceRe = re.compile(r"\s*$")


def isOnlyWhitespace(aString):
    return onlyWhitespaceRe.match(aString) is not None
