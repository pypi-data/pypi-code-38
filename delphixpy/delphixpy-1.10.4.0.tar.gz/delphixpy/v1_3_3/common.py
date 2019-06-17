# 
# Copyright 2014, 2019 by Delphix
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Module for simple generic operations without dependencies.
"""

import sys

_PYTHON_MAJOR_VERSION = sys.version_info[0]


def properties_for_obj(obj):
    """
    Returns a list of all properties for an object.
    """
    return [prop for prop in dir(obj) if prop_for_class(obj.__class__, prop)]


def prop_for_class(cls, prop):
    """
    Returns True if prop is a property in cls or in its ancestors
    """
    if hasattr(cls, prop) and isinstance(getattr(cls, prop), property):
        return prop
    else:
        if cls.__name__ == 'object':
            return None
        else:
            return prop_for_class(cls.__bases__[0], prop)


def _public_vars_for_obj(obj):
    return [v for v in sorted(obj.__dict__.keys())
            if not v.startswith('_')]


def generate_repr_string(obj):
    """
    Generates a __repr__ string for the python object 'obj'.
    Only properties and public instance variables are included.
    The string format is "ClassName(prop1=val1, prop2=val2, ...)"
    where the properties and instance variables are ordered
    alphabetically by name.
    """
    name = obj.__class__.__name__
    properties = properties_for_obj(obj)
    public_vars = _public_vars_for_obj(obj)
    prop_and_var_strings = []
    for v in sorted(properties + public_vars):
        key = repr(getattr(obj, v))
        prop_and_var_strings.append("%s=%s" % (v, key))
    return "%s(%s)" % (name, ", ".join(prop_and_var_strings))


def validate_format(*_arg):
    """
    This method can be overridden with format validation logic.
    """
    return True


def bytes_to_str(b):
    if _PYTHON_MAJOR_VERSION < 3:
        return str(b)
    else:
        return str(b, 'utf-8')