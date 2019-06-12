#
# Copyright 2014-2019 Martin Owens <doctormo@gmail.com>
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
The XSD Validator module for taking python, json or xml data trees and validating
them against XSD definitions.
"""

__version__ = '0.8'
__pkgname__ = 'xssd'

import re
import os
import copy
import json
import logging
from decimal import Decimal
from operator import lt, gt, le, ge

from datetime import datetime
from .parse import ParseXML
from .base import MODE_AND, MODE_OR
from .errors import (
    NoData, NoRootDocument, ElementErrors, NoTypeFound,
    NO_ERROR, EMPTY_OK, CRITICAL,
    INVALID_TYPE, INVALID_PATTERN, INVALID_MATCH, INVALID_VALUE,
    INVALID_MINLENGTH, INVALID_MAXLENGTH, INVALID_MIN_RANGE, INVALID_MAX_RANGE,
    INVALID_ENUMERATION, INVALID_FRACTION, INVALID_NUMBER, INVALID_COMPLEX,
    INVALID_REQUIRED, INVALID_EXIST, INVALID_MIN_OCCURS, INVALID_MAX_OCCURS,
    INVALID_XPATH, INVALID_CUSTOM, INVALID_DATE_FORMAT, INVALID_DATE,
)

def test_datetime(data, stype=None):
    """Test to make sure it's a valid datetime"""
    try:
        if '-' in data and ':' in data:
            datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
        elif '-' in data:
            datetime.strptime(data, "%Y-%m-%d")
        elif ':' in data:
            datetime.strptime(data, "%H:%M:%S")
        else:
            return INVALID_DATE_FORMAT()
    except ValueError:
        return INVALID_DATE()
    return NO_ERROR()

def max_digits(number, count):
    """Return true if the number of digits is equal"""
    return -Decimal(number).as_tuple().exponent > count

NUM_SIZE_TESTS = [
    ('minInclusive', lt, INVALID_MIN_RANGE),
    ('maxInclusive', gt, INVALID_MAX_RANGE),
    ('minExclusive', le, INVALID_MIN_RANGE),
    ('maxExclusive', ge, INVALID_MAX_RANGE),
    ('fractionDigits', max_digits, INVALID_FRACTION),
]

#Primitive types: [ anyURI, base64Binary,
#  decimal, duration, float, hexBinary,
#  gDay, gMonth, gMonthDay, gYear, gYearMonth, NOTATION, QName ]

BASE_CLASSES = {
    'complexTypes': {},
    'simpleTypes': {
        'string':     {'pattern': r'.*'},
        'integer':    {'pattern': r'[\-]{0,1}\d+'},
        'index':      {'pattern': r'\d+'},
        'double':     {'pattern': r'[0-9\-\.]*'},
        'token':      {'pattern': r'\w+', 'base': 'string'},
        'boolean':    {'pattern': r'1|0|true|false'},
        'email':      {'pattern': r'.+@.+\..+'},
        'date':       {'pattern': r'\d\d\d\d-\d\d-\d\d', 'base': 'datetime'},
        'time':       {'pattern': r'\d\d:\d\d:\d\d', 'base': 'datetime'},
        'datetime':   {'pattern': r'(\d\d\d\d-\d\d-\d\d)?[T ]?(\d\d:\d\d:\d\d)?',
                       'custom' : test_datetime},
        'percentage': {'base'    : r'double', 'minInclusive' : 0, 'maxInclusive' : 100},
    }
}

class Validator(object):
    """Validation Machine, parses data and outputs error structures.

    validator = Validator(definition, strict_root, strict_values)

    definition   - Validation structure (see main documentation)
    strict_root  - Don't automatically add a root element dictionary.
    strict_exist - Add errors for elements and attributes not in the schema.

    """
    def __init__(self, definition, strict_root=False, strict_exist=True, debug=False):
        self._strict_root = strict_root
        self._strict_exist = strict_exist
        self._definition = copy.deepcopy(BASE_CLASSES)
        self._debug = debug
        self.current_root_data = None

        self.load_definition_from_file(definition)

    def validate(self, data):
        """
        Validate a set of data against this validator.
        Returns an errors structure or 0 if there were no errors.
        """
        data = self._load_file(data)

        if data is None:
            raise NoData("Data must be present in order to validate.")

        if not isinstance(data, dict):
            raise ValueError("Invalid data type: {}".format(type(data).__name__))

        # Save the root data for this validation so it can be
        # used for xpath queries later on in the validation.
        self.current_root_data = data

        if 'root' not in data:
            if not self._strict_root:
                # Add root back in, in order to validate it.
                ret = self.validate({'root': data})
                # Remove root from results too for consistancy
                return ret['root'] if ret and 'root' in ret else ret
            # No root and root checking is switched on.
            raise NoRootDocument("Root of data is missing")

        if 'root' not in self._definition:
            # Adding in a root is done in the load_definition section.
            raise NoRootDocument("Root of schema is missing.")

        return self._validate_elements(self._definition['root'], data['root'])

    def load_definition(self, definition):
        """Internal method for loading a definition into the validator."""
        includes = definition.pop('include', [])

        # Make sure we have base classes in our definition.
        self.update_types(definition)

        if 'root' not in self._definition:
            if 'root' in definition:
                self._definition['root'] = definition['root']
            elif not self._strict_root:
                if 'complexTypes' not in definition and 'simpleTypes' not in definition:
                    # This means the definition contains no root, no types so it's
                    # probably a rootless definition
                    self._definition['root'] = definition
        elif 'root' in definition:
            raise KeyError("Can not overwrite existing root definition with new one.")

        # Now add any includes (external imports)
        for filename in includes:
            include = None
            if isinstance(filename, str):
                include = self.load_definition_from_file(filename)
            elif isinstance(filename, dict):
                include = filename
            if include:
                self.update_types(include)
            else:
                raise Exception("Can't load include: %s" % str(filename))
        return definition

    def update_types(self, source):
        """Update both simple and compelx types."""
        for tkey in ('simpleTypes', 'complexTypes'):
            self._definition.setdefault(tkey, {}).update(source.get(tkey, {}))

    def load_definition_from_file(self, filename):
        """Internal method for loading a definition from a file"""
        return self.load_definition(self._load_file(filename, True))

    def _validate_elements(self, definition, data, mode=MODE_AND, primary=True):
        """Internal method for validating a list of elements"""
        errors = ElementErrors(mode)

        # This should be AND or OR and controls the logic flow of the data varify
        if mode not in (MODE_AND, MODE_OR):
            raise Exception("Invalid mode '%s', should be MODE_AND or MODE_OR." % mode)

        if not isinstance(definition, list):
            raise Exception("Definition is not in the correct format:"
                            " expected list (got %s)." % type(definition))

        for element in definition:
            # Element data check
            if isinstance(element, dict):
                name = element.get('name', None)
                # Skip element if it's not defined
                if not name:
                    logging.warn("Skipping element, no name")
                    continue
                # We would pass in only the data field selected, but we need everything.
                errors[name] = self._validate_element(element, data, name)
            elif isinstance(element, list):
                errors.update(self._validate_elements(element, data, not mode, False))
            else:
                logging.warning("This is a complex type, but isn't element.")

        # These are all the left over names
        if self._strict_exist and primary:
            for name in data.keys():
                if name not in errors:
                    errors[name] = INVALID_EXIST(name)

        return errors

    def _validate_element(self, definition, all_data, name):
        """Internal method for validating a single element"""
        results = []
        proped = False

        data = all_data.get(name, None)
        if data != None and not isinstance(data, list):
            proped = True
            data = [data]

        min_occurs = int(definition.get('minOccurs', 1))
        max_occurs = definition.get('maxOccurs', 1)
        data_type = definition.get('type', 'string')
        default = definition.get('default', None)
        fixed = definition.get('fixed', None)

        # minOccurs checking
        if min_occurs >= 1:
            if data != None:
                if min_occurs > len(data):
                    return INVALID_MIN_OCCURS()
            elif default != None:
                data = [default]
            else:
                return INVALID_REQUIRED()
            if max_occurs not in [None, 'unbounded'] and int(max_occurs) < min_occurs:
                max_occurs = min_occurs
        elif data is None:
            # No data and it wasn't required
            return EMPTY_OK()

        # maxOccurs Checking
        if max_occurs != 'unbounded':
            if int(max_occurs) < len(data):
                return INVALID_MAX_OCCURS()

        for element in data:
            # Fixed checking
            if fixed != None:
                if not isinstance(element, str) or element != fixed:
                    results.append(INVALID_VALUE)
                    continue
            # Default checking
            if default is not None and element is None:
                element = default

            # Match another node
            match = definition.get('match', None)
            not_match = definition.get('notMatch', None)
            if match != None:
                value = self._find_value(match, all_data)
                if value != element:
                    return INVALID_MATCH((value, element))
            if not_match != None:
                value = self._find_value(not_match, all_data)
                if value == element:
                    return INVALID_MATCH((value, element))

            opts = {}
            for option in ('minLength', 'maxLength', 'complexType'):
                opts[option] = definition.get(option, None)

            # Element type checking
            result = self._validate_type(data_type, element, **opts)
            if result:
                results.append(result)

        if results:
            if proped:
                return results[0]
            return results
        return NO_ERROR()

    def _validate_type(self, type_name, data, **opts):
        """Internal method for validating a single data type"""
        definition = self._definition
        simple_type = definition['simpleTypes'].get(type_name, None)
        complex_type = definition['complexTypes'].get(
            type_name, opts.get('complexType', None))

        if isinstance(data, bool):
            data = str(data).lower()

        if complex_type:
            if isinstance(data, dict):
                return self._validate_elements(complex_type, data)
            return INVALID_COMPLEX()
        elif simple_type:
            simple_type = simple_type.copy()
            simple_type.update(opts)
            return self._validate_simple(type_name, simple_type, data)
        raise NoTypeFound("Can't find type '%s'" % type_name)

    def _validate_simple(self, type_name, simple_type, data):
        """Validate the simple type definition against the data"""
        base = simple_type.get('base', None)
        pattern = simple_type.get('pattern', None)
        custom = simple_type.get('custom', None)

        # Base type check
        if base:
            err = self._validate_type(base, data)
            if err:
                return err

        # Pattern type check, assumes edge detection
        if pattern:
            try:
                if not re.match("^%s$" % pattern, str(data)):
                    return INVALID_PATTERN((pattern, data))
            except TypeError:
                return INVALID_PATTERN((type_name, type(data)))

        # Custom method check
        if custom:
            if not callable(custom):
                return INVALID_CUSTOM()
            failure = custom(data, simple_type)
            if failure:
                return failure

        # Length check is intergrated into min and max lengths
        length = simple_type.get('length', None)
        max_length = simple_type.get('maxLength', None) or length
        min_length = simple_type.get('minLength', None) or length

        # Maximum Length check
        if max_length != None and len(data) > int(max_length):
            return INVALID_MAXLENGTH()

        # Minimum Length check
        if min_length != None and len(data) < int(min_length):
            return INVALID_MINLENGTH()

        # Check Enumeration
        enum = simple_type.get('enumeration', None)
        if enum:
            if not isinstance(enum, list):
                raise Exception("Validator Error: Enumberation not a list")
            if data not in enum:
                return INVALID_ENUMERATION()

        # This over-writes the data, so be careful
        try:
            data = int(data)
        except ValueError:
            pass

        for name, opr, err in NUM_SIZE_TESTS:
            test = simple_type.get(name, None)
            if test != None:
                if not isinstance(data, int):
                    return INVALID_NUMBER()
                if opr(data, test):
                    return err
        return NO_ERROR()

    def _find_value(self, path, data):
        """Internal method for finding a value match (basic xpath)"""
        # Remove root path, and stop localisation
        if path[0] == '/':
            data = self.current_root_data
            paths = path[1:].split('/')
        else:
            paths = path.split('/')

        for segment in paths:
            if isinstance(data, dict):
                try:
                    return data[segment]
                except KeyError:
                    pass
            return INVALID_XPATH(path)
        return data

    @staticmethod
    def _load_file(filename, definition=False):
        """
        Internal method for loading a file, must be valid perl syntax.
        Yep that's right, be bloody careful when loading from files.
        """
        if isinstance(filename, (dict, list, tuple)):
            return filename

        if not os.path.exists(filename):
            raise Exception("file doesn't exist: %s" % filename)

        with open(filename, 'r') as fhl:
            content = fhl.read()

        if content[0] == '<':
            # XML File, parse and load
            parser = ParseXML(filename)
            if definition and 'XMLSchema' in content:
                return parser.definition
            return parser.data
        return json.loads(content)

    def explain_validation(self, data):
        """
        Do a validation but reduce the errors to a message string and return it.
        """
        return self.validate(data).explain()

    @staticmethod
    def explain(errors, *args, **kwargs):
        """Backwards compatible, now use errors.explain(...)"""
        return errors.explain(*args, **kwargs)
