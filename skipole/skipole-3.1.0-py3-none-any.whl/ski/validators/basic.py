

"""This module contains basic validation functions

Each Validator is a class, with a _check method

"""


import re
from . import Validator

from ..excepts import ValidateError

# a search for anything none-alphanumeric and not an underscore
_AN = re.compile('[^\w]')

# a search for anything none-alphanumeric, not a dot and not an underscore
_AND = re.compile('[^\w\.]')


class AllowedValuesOnly(Validator):
    "Checks the value is in the allowed values only"

    arg_descriptions = {}   # Takes no arguments

    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        """Item must be one of the allowed values, so this invalidates"""
        return '', False


class NoOperation(Validator):
    "Always passes"

    arg_descriptions = {}   # Takes no arguments

    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        """Item always validates"""
        return item, True


class AllowedValuesOrEmpty(Validator):
    "Checks the value is in the allowed values or is empty"

    arg_descriptions = {}   # Takes no arguments

    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        if not item:
            return '', True
        return '', False


class MinLength(Validator):
    "Checks field length is equal or greater than the minimum value given"

    arg_descriptions = {'minlength':1}


    def __setitem__(self, arg_name, value):
        "Sets an argument value"
        Validator.__setitem__(self, arg_name, value)
        try:
            intval = int(value)
        except Exception:
            raise ValidateError(message = 'minlength value must be an integer')
        if intval < 0:
            raise ValidateError(message = 'A minimum value of least 0 is expected')
        self._val_args[arg_name] = intval


    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        if len(item) < self["minlength"]:
            return '', False
        return item, True


class MaxLength(Validator):
    "Checks field length is equal or less than the maximum value given"

    arg_descriptions = {'maxlength':50}

    def __setitem__(self, arg_name, value):
        "Sets an argument value"
        Validator.__setitem__(self, arg_name, value)
        try:
            intval = int(value)
        except Exception:
            raise ValidateError(message = 'maxlength value must be an integer')
        if intval < 1:
            raise ValidateError(message = 'A maximum value of of at least 1 is expected')
        self._val_args[arg_name] = intval

    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        if len(item) > self["maxlength"]:
            return '', False
        return item, True


class NotEmpty(Validator):
    "Raises an error if a field is empty"

    arg_descriptions = {}   # Takes no arguments

    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        if item is False:
            # False is not an empty field
            return item, True
        if item is 0:
            # 0 is not an empty field
            return item, True
        if not item:
            return '', False
        return item, True


class IntMinMax(Validator):
    """Check integer, limit value to between min and max value, raise error if input not an integer string
       but if it is, and is beyond the range, then does not raise an error, just limits the integer size"""

    arg_descriptions = {'maxval':255,
                        'minval':0}


    def __setitem__(self, arg_name, value):
        "Sets an argument value"
        Validator.__setitem__(self, arg_name, value)
        try:
            intval = int(value)
        except Exception:
            raise ValidateError(message = 'values given must be integers')
        if arg_name == 'maxval':
            if intval < 1:
                raise ValidateError(message = 'A maximum value of of at least 1 is expected')
        if arg_name == 'minval':
            if intval < 0:
                raise ValidateError(message = 'A minimum value of least 0 is expected')
        self._val_args[arg_name] = intval

    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        try:
            i = int(item)
        except Exception:
            return '', False
        if self["maxval"] < self["minval"]:
            return '', False
        if i > self["maxval"]:
            return str(self["maxval"]), False
        if i < self["minval"]:
            return str(self["minval"]), False
        return str(i), True


class AlphaNumUnder(Validator):
    "Checks the value is alphanumric or underscore only"

    arg_descriptions = {}   # Takes no arguments

    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        "Return item, True if item is alphanumeric or underscore only"
        if  _AN.search(item):
            return '', False
        return item, True


class AlphaNumDotUnder(Validator):
    "Checks the value is alphanumric, dot or underscore only"

    arg_descriptions = {}   # Takes no arguments

    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        "Return item, True if item is alphanumeric or underscore only"
        if  _AND.search(item):
            return '', False
        return item, True


class Search(Validator):
    """Check item against a regular expresion"""

    arg_descriptions = {'pattern':"[\s\S]"}


    def __setitem__(self, arg_name, value):
        "Sets an argument value"
        Validator.__setitem__(self, arg_name, value)
        if not value:
            raise ValidateError(message = 'A regular expression must be given')
        self._val_args[arg_name] = value

    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        "Return item, True if pattern search successfull"
        if re.search(self._val_args['pattern'],item) is None:
            return '', False
        return item, True


