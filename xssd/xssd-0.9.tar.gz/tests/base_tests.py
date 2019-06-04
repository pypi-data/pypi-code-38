#
# Copyright 2010 Martin Owens
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
Base classes for testing data structures.
"""

import unittest

from xssd import Validator

class BaseFileTest(unittest.TestCase):
    """Base test for testing data sets"""
    definition = None # Definition

    def setUp(self):
        self.validator = Validator(self.definition)

    def positive_test(self, data):
        """Positive test"""
        errors = self.validator.validate(data)
        self.assertFalse(errors, 'Expected Pass (%s)' % str(errors))

    def negative_test(self, data, against=None):
        """Negative test"""
        errors = self.validator.validate(data)
        if against is not None:
            self.assertEqual(errors, against)
        self.assertTrue(errors, 'Expected Errors (%s)' % str(errors))

class StaticError(KeyError):
    """Error used when trying to modify a static object"""

class Static(object):
    def __new__(cls, data):
        if data is None:
            return data
        elif isinstance(data, dict):
            return StaticDict(data)
        elif isinstance(data, (list, tuple)):
            return StaticList(data)
        elif isinstance(data, (int, float, str)):
            return data
        raise TypeError("Unknown data type for static creation: {}".format(type(data)))

class StaticList(list):
    """Like a normal list, but modifying it will cause an error"""
    def __init__(self, data):
        data = [Static(item) for item in data]

    def __setitem__(self, key, value):
        raise StaticError("Tried to set an item into a static list.")

    def __delitem__(self, key):
        raise StaticError("Tried to delete an item from a static list.")

class StaticDict(dict):
    """Like a normal dictionary, but modifiying it will cause an error"""
    def __setitem__(self, key, value):
        raise StaticError("Tried to set an item into a static dictionary.")

    def __delitem__(self, key):
        raise StaticError("Tried to delete an item from a static dictionary.")
