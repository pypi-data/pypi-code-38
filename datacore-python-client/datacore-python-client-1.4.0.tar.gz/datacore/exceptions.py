"""
This module defines the custom exception for this module.

Author: Vincent Medina, EveryMundo, 2016
Email: vincent@everymundo.com
"""
# Standard library packages
from typing import Any, AnyStr


# Package Exception
class DatacoreException(Exception):
    """
    Datacore exception handler, base class.
    This is a very basic error handler specific to this module.
    """
    def __init__(self, code: AnyStr, message: AnyStr, other: Any=None, *args, **kwargs) \
            -> None:
        """
        :param code: BriefErrorMsg
        :param message: Error message in more verbose detail.
        """
        self.code = code
        self.message = message
        self.other = other
        super().__init__(code, message, *args, **kwargs)

    def __str__(self, *args, **kwargs) -> str:
        """
        Sets the human readable string casting of this class. Overrides Exception.__str__().
        :param args:
        :param kwargs:
        :return:
        """
        string = "{c}, {r}".format(c=self.code, r=self.message)
        if self.other:
            string += ", {o}".format(o=self.other)
        if args:
            string += ", {a}".format(a=args)
        if kwargs:
            string += ", {k}".format(k=kwargs)
        return string

    @classmethod
    def from_error(cls, error: Exception, code: AnyStr=None, message: AnyStr=None, other=None) -> "DatacoreException":
        """
        This returns an exception from an existing error object.
        :param error:
        :param code:
        :param message:
        :return:
        """
        # If we do not have code or message, synthesize them from the error args
        if not code:
            code = error.args[0]
        if not message:
            message = error.args[1]
        # Extract the args
        args = error.args
        # Return exception object
        exception = DatacoreException(code, message, other, *args)
        # But first create its traceback.
        exception.__traceback__ = error.__traceback__
        return exception


class DatacoreTypeError(DatacoreException):
    """
    For specific type errors.
    """
    def __init__(self, code: AnyStr, reason: AnyStr, *args, **kwargs):
        """
        Same constructor as DatacoreException
        :param code:
        :param reason:
        :param args:
        :param kwargs:
        """
        super().__init__(code, reason, *args, **kwargs)