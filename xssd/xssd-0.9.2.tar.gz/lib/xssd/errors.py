#
# Copyright 2010-2019 Martin Owens
#
# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
#
"""
Structural Errors which track complex errors throughout a complex structure.

This includes array and dictonary problems, but errors do not stop the parsing
and validation of the rest of the structure.

These are no python-errors as they are not code errors but data error report codes.
"""

from .base import MODE_AND, MODE_OR

class NoData(ValueError):
    """Report error about there not being any data"""

class NoRootDocument(ValueError):
    """Report error concerning the lack of root"""

class NoTypeFound(KeyError):
    """Reported when there the named type is not found"""

class ElementErrors(dict):
    """Keep track of errors as they're added, true if errors."""
    def __init__(self, mode=MODE_AND):
        super(ElementErrors, self).__init__()
        self._in_error = 0
        self._added = 0
        self._mode = mode

    def __setitem__(self, key, value):
        if key in self:
            self.remove_error(self[key])
        super(ElementErrors, self).__setitem__(key, value)
        self.add_error(value)

    def __repr__(self):
        if self._added and not self._in_error:
            return "NO_ERROR"
        return super(ElementErrors, self).__repr__()

    def get_mode(self):
        """Return the current mode for this error set"""
        return self._mode

    def pop(self, key):
        self.remove_error(super(ElementErrors, self).pop(key))

    def update(self, errors):
        """Merge in errors from a seperate validation process"""
        # Adding a batch of errors is counted as one.
        self.add_error(errors)
        if isinstance(errors, ElementErrors):
            if errors.get_mode() == MODE_OR and not errors:
                errors = dict(itm for itm in errors.items() if itm[1] == NO_ERROR)
            else:
                errors = dict(itm for itm in errors.items() if itm[1] != INVALID_EXIST)
        super(ElementErrors, self).update(errors)

    def add_error(self, error):
        """Record the number of errors, and the number in error (positive errors)"""
        if error:
            self._in_error += 1
        self._added += 1

    def remove_error(self, error):
        """Remove the record of a previouslly added error (negative of add_error)"""
        if error:
            self._in_error -= 1
        self._added -= 1

    def __nonzero__(self):
        #print "In ERROR: %s %i:%i" % (str(self._data), self._in_error, self._added)
        if self._mode == MODE_OR:
            if self._added > 0:
                return self._in_error >= self._added
            return False
        return self._in_error != 0

    def __bool__(self):
        "PY3 for nonzero"
        return self.__nonzero__()

    def __eq__(self, errors):
        if not isinstance(errors, dict):
            return False
            #raise ValueError("Can't compare error dictionary with %s" % type(errors))
        for (key, value) in super(ElementErrors, self).items():
            if key not in errors or errors[key] != value:
                return False
        return True

    def __ne__(self, opt):
        return not self.__eq__(opt)

    @classmethod
    def label(cls):
        """Returns a fixed label for collection of errors"""
        return "contains_errors"

    def explain(self, no_errors=False, level=1):
        """
        Convert errors into a message useful to humans
        """
        pad = '  ' * level
        messages = []
        if self:
            for name, error in self.items():
                if isinstance(error, ElementErrors):
                    child_errors = error.explain(no_errors=no_errors, level=level+1)
                    if child_errors:
                        messages.append(pad + "+ {} - Children have errors\n".format(name))
                        messages.extend(child_errors)
                elif isinstance(error, (tuple, list)):
                    raise ValueError("Not sure how to deal with {}".format(error))
                elif no_errors or error:
                    messages.append(error.explain(level=level, name=name))
        if level == 1:
            return ''.join(messages)
        return messages


class ValidateError(str):
    """Control the validation errrors and how they're displayed"""
    code = None
    desc = None
    name = None

    @classmethod
    def new(cls, code, name, desc=None):
        """Create a validate error class"""
        return type(name, (cls,), {'desc': desc, 'code': code, 'name': name})

    def __init__(self, context=None):
        self.context = context
        super().__init__()

    def __str__(self):
        return self.name.upper().replace(' ', '_')

    def __int__(self):
        return self.code

    def __repr__(self):
        result = [self.name]
        if self.context:
            result.append('{' + str(self.context) + '}')
        if self.desc:
            result.append('"' + self.desc + '"')
        return ' '.join(result)

    def __nonzero__(self):
        # PY2 for __bool__
        return self.__bool__()

    def __bool__(self):
        return self.code > 0

    def __eq__(self, opt):
        if isinstance(opt, ValidateError):
            opt = opt.getcode()
        return self.getcode() == opt

    def __ne__(self, opt):
        return not self.__eq__(opt)

    def getcode(self):
        """Returns the error code"""
        return self.code

    def debug(self):
        """Used for debugging"""
        if self.context:
            return "%s (%s)\n" % (self.name, str(self.context))
        return "#%d %s (%s)\n" % (self.code, self.name, self.desc)

    def explain(self, level=0, name='root'):
        """Return this part of the explaination"""
        return ('  ' * level) + "* {} - {}".format(name, self.debug())

    @classmethod
    def label(cls):
        return cls.name.lower().replace(' ', '_')

# Validation Error codes
NO_ERROR = ValidateError.new(0x00, 'No Error')
EMPTY_OK = ValidateError.new(0x00, 'Empty but OK')
INVALID_TYPE = ValidateError.new(0x01, 'Invalid Node Type')
INVALID_PATTERN = ValidateError.new(0x02, 'Invalid Pattern', 'Regex Pattern failed')
INVALID_MINLENGTH = ValidateError.new(0x03, 'Invalid MinLength', 'Not enough nodes present')
INVALID_MAXLENGTH = ValidateError.new(0x04, 'Invalid MaxLength', 'Too many nodes present')
INVALID_MATCH = ValidateError.new(0x05, 'Invalid Match', 'Node to Node match failed')
INVALID_VALUE = ValidateError.new(0x06, 'Invalid Value', 'Fixed string did not match')
INVALID_NODE = ValidateError.new(0x07, 'Invalid Node', 'Required data does not exist for this node')
INVALID_ENUMERATION = ValidateError.new(0x08, 'Invalid Enum', 'Data not equal to any values')
INVALID_MIN_RANGE = ValidateError.new(0x09, 'Invalid Min Range', 'Less than allowable range')
INVALID_MAX_RANGE = ValidateError.new(0x0A, 'Invalid Max Range', 'Greater than allowable range')
INVALID_FRACTION = ValidateError.new(0x12, 'Invalid Fraction', 'Fraction is not the right format.')
INVALID_NUMBER = ValidateError.new(0x0B, 'Invalid Number', 'Data is not a real number')
INVALID_COMPLEX = ValidateError.new(0x0C, 'Invalid Complex', 'Failed to validate Complex Type')
INVALID_REQUIRED = ValidateError.new(0x0D, 'Invalid Required', 'Data is required, but missing.')
INVALID_EXIST = ValidateError.new(0x0E, 'Invalid Exist', 'This data shouldn\'t exist.')
INVALID_MIN_OCCURS = ValidateError.new(0x0F, 'Invalid Occurs', 'Minium number of occurances not met')
INVALID_MAX_OCCURS = ValidateError.new(0x10, 'Invalid Occurs', 'Maxium number of occurances exceeded')
INVALID_XPATH = ValidateError.new(0x11, 'Invalid XPath', 'The path given doesn\'t exist.')

# When python goes wrong
CRITICAL = ValidateError.new(0x30, 'Critical Problem')

# Custom internal methods for checking values
INVALID_CUSTOM = ValidateError.new(0x40, 'Invalid Custom', 'Custom filter method returned false')

# Extra Error codes
INVALID_DATE_FORMAT = ValidateError.new(0x50, 'Invalid Date Format', 'Format of date can\'t be parsed')
INVALID_DATE = ValidateError.new(0x51, 'Invalid Date', 'Date is out of range or otherwise not valid')
