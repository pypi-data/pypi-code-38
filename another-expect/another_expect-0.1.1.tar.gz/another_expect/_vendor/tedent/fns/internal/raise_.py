from textwrap import dedent
from .isOnlyWhitespace import isOnlyWhitespace
import os


def raise_(errorClass, message, *, fromException=None):
    allLines = message.split(os.linesep)
    if isOnlyWhitespace(allLines[0]) and isOnlyWhitespace(allLines[-1]):
        message = dedent(message)

    err = errorClass(message)

    if fromException is None:
        raise err
    else:
        raise err from fromException
