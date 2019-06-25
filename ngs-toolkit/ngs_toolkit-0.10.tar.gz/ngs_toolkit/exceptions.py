#!/usr/bin/env python


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputError(Error):
    """
    Exception raised for errors in the input.

    Attributes
    ----------
        expr :
            Input expression in which the error occurred
        msg  : :obj:`str`
            Explanation of the error
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg


class UserInputError(InputError):
    """
    Exception raised for errors in the input caused by the user.

    Attributes
    ----------
        expr :
            Input expression in which the error occurred
        msg  : :obj:`str`
            Explanation of the error
    """
    pass
