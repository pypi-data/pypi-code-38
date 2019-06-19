# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import re
import six
import copy
import inspect
import sklearn
import sklearn.base
import numpy as np

from PySide import QtGui

from sympathy.api import table
from sympathy.platform.viewer import ListViewer
from sympathy.platform.table_viewer import TableViewer
from sylib.machinelearning.utility import value_to_tables
from sympathy.api.exceptions import sywarn

# from sylib.machinelearning.descriptors import BoolListType
# from sylib.machinelearning.descriptors import BoolType
# from sylib.machinelearning.descriptors import Descriptor
# from sylib.machinelearning.descriptors import FloatListType
# from sylib.machinelearning.descriptors import FloatType
# from sylib.machinelearning.descriptors import GenericListType
# from sylib.machinelearning.descriptors import IntListType
# from sylib.machinelearning.descriptors import IntType
# from sylib.machinelearning.descriptors import NoneType
# from sylib.machinelearning.descriptors import NumericType
# from sylib.machinelearning.descriptors import StringListType
# from sylib.machinelearning.descriptors import StringSelectionType
# from sylib.machinelearning.descriptors import StringType
# from sylib.machinelearning.descriptors import UnionType


class ParameterType(object):

    def test_value(self, val):
        """Verifies that given python object 'val' is a valid value"""
        raise NotImplementedError

    def create_param(self, params, name, description):
        """Creates a sympathy parameter definition corresponding to a
        string representation of this Parameter"""
        raise NotImplementedError

    def description(self):
        """Returns a textual description of the constraints imposed
        by this type"""
        raise NotImplementedError

    def from_string(self, string):
        """Creates an object of this type based on a string, if possible.
        Otherwise raises a ValueError"""
        raise NotImplementedError

    def to_string(self, value):
        """Creates string representation of this object. Object must first
        have passed a test_value check"""
        raise NotImplementedError


class NumericType(ParameterType):
    pass


class IntType(NumericType):
    def __init__(self, default=None, min_value=None, max_value=None,
                 allowed_values=None, validator=None, type_desc=None):
        self.min_value = min_value
        self.max_value = max_value
        self.allowed_values = allowed_values
        self.validator = validator
        self.type_desc = type_desc

        if default is None:
            self.default = min_value or 0
        else:
            self.default = default

    def test_value(self, val):
        if not isinstance(val, int):
            return False
        if self.validator is not None:
            return self.validator(val)
        if self.min_value is not None and self.min_value > val:
            return False
        if self.max_value is not None and self.max_value < val:
            return False
        if self.allowed_values is not None and val not in self.allowed_values:
            return False
        return True

    def create_param(self, params, name, description):
        if name not in params:
            params.set_string(name, value="{0}".format(self.default),
                              label=name, description=description)

    def description(self):
        if self.type_desc:
            return self.type_desc
        if self.allowed_values:
            return "integer in {0}".format(self.allowed_values)
        if self.min_value is None and self.max_value is None:
            return "integer"
        elif self.min_value is None and self.max_value is not None:
            return "integer <= {0}".format(self.max_value)
        elif self.min_value is not None and self.max_value is None:
            return "integer >= {0}".format(self.min_value)
        else:
            return "{0} <= integer <= {1}".format(
                self.min_value, self.max_value)

    def from_string(self, string):
        return int(string)

    def to_string(self, value):
        return "{0}".format(value)


class GenericListType(ParameterType):
    def __init__(self, default=0, min_value=None, max_value=None,
                 allowed_values=None, validator=None, type_desc=None,
                 min_length=None, max_length=None):
        self.min_value = min_value
        self.max_value = max_value
        self.allowed_values = allowed_values
        self.validator = validator
        self.type_desc = type_desc
        self.min_length = min_length
        self.max_length = max_length

        if default is None:
            self.default = [min_value or 0]
        else:
            self.default = default

    def test_value(self, values):
        if not isinstance(values, list):
            return False
        if self.validator is not None:
            return self.validator(values)
        for val in values:
            if self.min_value is not None and self.min_value > val:
                return False
            if self.max_value is not None and self.max_value < val:
                return False
            if (self.allowed_values is not None
                    and val not in self.allowed_values):
                return False
        if self.min_length is not None and len(values) < self.min_length:
            return False
        if self.max_length is not None and len(values) > self.max_length:
            return False
        return True

    def create_param(self, params, name, description):
        if name not in params:
            params.set_string(name, value=self.to_string(self.default),
                              label=name, description=description)

    def description(self):
        typename = self.__class__.typename
        name = typename
        if self.min_length is not None:
            name = "{0}".format(typename)
            for i in range(1, self.min_length):
                name += ", {0}".format(typename)
        if self.max_length is None:
            name += " [, ...]"
        elif self.max_length > self.min_length:
            name += " ["
            for i in range(self.min_length or 1, self.max_length):
                name += ", {0}".format(typename)
            name += "]"

        if self.type_desc:
            return self.type_desc
        if self.allowed_values:
            return "{1} in {0}".format(self.allowed_values, name)
        if self.min_value is None and self.max_value is None:
            return name
        elif self.min_value is None and self.max_value is not None:
            return "{1} <= {0}".format(self.max_value, name)
        elif self.min_value is not None and self.max_value is None:
            return "{1} >= {0}".format(self.min_value, name)
        else:
            return ("{0} <= {2} <= {1}"
                    .format(self.min_value, self.max_value, name))

    def from_string(self, string):
        separators = [',', ';', '\t']
        if not isinstance(string, six.string_types):
            string = str(string)
        string = string.strip()
        if string[0] == '[' and string[-1] == ']':
            string = string[1:-1]
        if string[0] == '(' and string[-1] == ')':
            string = string[1:-1]
        for separator in separators:
            string = string.replace(separator, ' ')
        return [self.convert(v) for v in string.split()]

    def to_string(self, values):
        if len(values) == 0:
            return ""
        text = "{0}".format(values[0])
        for v in values[1:]:
            text += ", {0}".format(v)
        return text


class IntListType(GenericListType):
    typename = "integer"

    def convert(self, s):
        return int(s)


class FloatListType(GenericListType):
    typename = "float"

    def convert(self, s):
        return float(s)


class StringListType(GenericListType):
    typename = "string"

    def convert(self, s):
        return s


class BoolListType(GenericListType):
    typename = "bool"

    def convert(self, s):
        if s == 'TRUE' or s == 'True' or s == 'true' or s is True:
            return True
        if s == 'FALSE' or s == 'False' or s == 'false' or s is False:
            return False
        raise ValueError


class FloatType(NumericType):

    def __init__(self, default=None, min_value=None, max_value=None,
                 allowed_values=None, validator=None, type_desc=None):
        self.min_value = min_value
        self.max_value = max_value
        self.allowed_values = allowed_values
        self.validator = validator
        self.type_desc = type_desc

        if default is None:
            self.default = min_value or 0
        else:
            self.default = default

    def test_value(self, val):
        if not isinstance(val, float):
            return False
        if self.validator is not None:
            return self.validator(val)
        if self.min_value is not None and self.min_value > val:
            return False
        if self.max_value is not None and self.max_value < val:
            return False
        if self.allowed_values is not None and val not in self.allowed_values:
            return False
        return True

    def create_param(self, params, name, description):
        if name not in params:
            params.set_string(
                name, value="{0}".format(self.default), label=name,
                description=description)

    def description(self):
        if self.type_desc:
            return self.type_desc
        if self.allowed_values:
            return "float in {0}".format(self.allowed_values)
        if self.min_value is None and self.max_value is None:
            return "float"
        elif self.min_value is None and self.max_value is not None:
            return "float <= {0}".format(self.max_value)
        elif self.min_value is not None and self.max_value is None:
            return "float >= {0}".format(self.min_value)
        else:
            return "{0} <= float <= {1}".format(self.min_value, self.max_value)

    def from_string(self, string):
        return float(string)

    def to_string(self, value):
        return "{0}".format(value)


class BoolType(NumericType):
    def __init__(self, default=False):
        self.default = default

    def test_value(self, val):
        return isinstance(val, bool)

    def create_param(self, params, name, description):
        if name not in params:
            params.set_string(name, value=self.to_string(self.default),
                              label=name, description=description)

    def description(self):
        return "boolean"

    def from_string(self, string):
        string = string.lower()
        if string == 'true':
            return True
        elif string == 'false':
            return False
        else:
            raise ValueError

    def to_string(self, value):
        return "{0}".format(value)


class StringType(ParameterType):
    def __init__(self, default=None):
        if default is not None:
            self.default = default
        else:
            self.default = ""

    def test_value(self, val):
        return True

    def create_param(self, params, name, description):
        if name not in params:
            params.set_string(name, value=self.to_string(self.default),
                              label=name, description=description)

    def description(self):
        text = 'string'
        return text

    def from_string(self, string):
        return string

    def to_string(self, value):
        return "{0}".format(value)


class StringSelectionType(StringType):
    def __init__(self, options, default=None):
        self.options = options
        if default is not None:
            self.default = default
        else:
            self.default = options[0]

    def test_value(self, val):
        try:
            return val in self.options
        except TypeError:
            return False

    def description(self):
        text = self.options[0]
        for opt in self.options[1:]:
            text = text+", "+opt
        return text

    def from_string(self, string):
        try:
            string = string.lower()
        except AttributeError:
            raise ValueError
        for opt in self.options:
            if string == opt.lower():
                return opt
        raise ValueError


class NoneType(ParameterType):
    def __init__(self):
        self.default = None

    def test_value(self, val):
        return val is None

    def create_param(self, params, name, description):
        if name not in params:
            params.set_string(name, value=self.to_string(None), label=name,
                              description=description)

    def description(self):
        return "None"

    def from_string(self, string):
        if string == "":
            return None
        if string is None:
            return None
        if string.lower() == 'none':
            return None
        raise ValueError

    def to_string(self, value):
        return "{0}".format(value)


class UnionType(ParameterType):
    def __init__(self, types, default=None):
        self.types = types
        self.default = default

    def test_value(self, val):
        for type_ in self.types:
            if type_.test_value(val):
                return True
        return False

    def create_param(self, params, name, description):
        if name not in params:
            params.set_string(name, value="{0}".format(self.default),
                              label=name, description=description)

    def description(self):
        text = "either: "
        is_first = True
        for type_ in self.types:
            if not is_first:
                text = text+"            \n    OR  "
            is_first = False
            text = text+type_.description()
        return text

    def from_string(self, string):
        for type_ in self.types:
            try:
                return type_.from_string(string)
            except ValueError:
                pass
        raise ValueError

    def to_string(self, value):
        for type_ in self.types:
            if type_.test_value(value):
                return type_.to_string(value)
        raise ValueError


class Descriptor(object):

    def __init__(self):
        self.name = "Model"

        # Dict mapping parameter names to their documentation
        # (the 'desc' string)
        self.descriptions = {}
        # Dict mapping parameter names to their types
        self._types = {}
        # Dict mapping parameter names to their full definitions
        # (dictionaries with 'name', 'desc'...)
        self._parameters = {}
        # List of dictionaries containing: name, desc of attributes
        self._attributes = []

        self.mirror_xy_names = False
        self._x_names = None
        self._y_names = None
        # _xout_names intentionally not initialized, fallback to y_names when
        # not given. These names are only used by transform nodes that can
        # also act as classifiers

    def new(self):
        return copy.copy(self)

    def set_info(self, info, doc_class=None):
        """
        Takes a list of dictionaries or lists of itself recursively that
        together gives all information about the parameters described by
        this descriptor object.

        Each dictionary should contain the following keys:
        - name: the name of this parameter
        - desc: the description of this parameter
        - type: the type of this parameter using one of the special
                type constructors
        """

        self.info = info
        self.descriptions = {}
        self._types = {}
        self._parameters = {}

        def process_info(info):
            if isinstance(info, list):
                return list(map(process_info, info))
            elif isinstance(info, six.string_types):
                # Strings inside lists act as names of parameter groups
                return None
            elif not isinstance(info, dict):
                raise ValueError

            # Attempt to automatically extract documentation from the
            # corresponding sklearn docstring
            if 'desc' not in info and doc_class is not None:
                info['desc'] = self.lookup_doc(
                    'Parameters', info['name'], doc_class, skip_first=True)
            elif 'desc' in info and not isinstance(info['desc'],
                                                   six.string_types):
                info['desc'] = self.lookup_doc(
                    'Parameters', info['name'], info['desc'], skip_first=True)
            else:
                pass

            self.descriptions[info['name']] = info['desc']
            self._types[info['name']] = info['type']
            if 'skl_name' not in info:
                info['skl_name'] = info['name']
            self._parameters[info['name']] = info

        process_info(info)

    @property
    def parameters(self):
        return self._parameters

    @property
    def types(self):
        return self._types

    @property
    def attributes(self):
        return self._attributes

    def lookup_doc(self, sec_name, name, obj, skip_first=False):
        """Extracts and formats documentation for 'name:' from docstring"""
        s = obj.__doc__
        s = s[s.find(sec_name):]
        idx = s.find("{} :".format(name))
        if idx < 0:
            idx = s.find("`{}` :".format(name))
        s = s[idx:]

        # Calculate indentation level of actual content (not counting
        # first line) or any empty lines
        pos = s.find('\n')
        if len(s) - pos <= 1:
            return ''
        while s[pos] == '\n':
            pos = pos + 1
        for level in range(len(s)-pos):
            if s[pos+level] != ' ':
                break

        if level == 0:
            raise ValueError(
                "Failed to extra documentation for {} from {}"
                .format(name, obj))

        # Find point where indentation < level, stop string there
        pos = 0
        while pos + 1 < len(s):
            if s[pos] == '\n' and s[pos+1] != '\n':
                if s[pos+1:pos+level+1] != ' '*level:
                    break
                pos += level or 1
            else:
                pos += 1
        s = s[:pos]
        # Remove first line and indentation, if wanted
        if skip_first:
            s = s[s.find('\n'):].replace('\n'+' '*level, '\n')[1:]
        # Remove bibliography references (numbers within brackets. eg. [4])
        s = re.sub(r'\[\d+\]', '', s)
        # Remove glossary references eg: :term:`something <something>`
        s = re.sub(r':term:`(.*)<(.*)>`', r'\g<2>', s)
        # Remove other references, it is unlikely that we can resolve them!
        s = re.sub(r':ref:`(.*)`', r'\g<1>', s)

        # Fix a bug in sklearn documentation 0.20.0
        if name == 'n_jobs':
            s = s.replace('multi_class=\'ovr\'\".', 'multi_class=\'ovr\'.')
        return s

    def set_attributes(self, attr, doc_class=None):
        for attribute in attr:
            if ('desc' not in attribute and doc_class is not None):
                attribute['desc'] = self.lookup_doc(
                    'Attributes', attribute['name'],
                    doc_class, skip_first=True)
            elif ('desc' in attribute
                  and not isinstance(attribute['desc'], six.string_types)):
                attribute['desc'] = self.lookup_doc(
                    'Attributes', attribute['name'], attribute['desc'],
                    skip_first=True)
            elif 'desc' not in attribute:
                attribute['desc'] = ''
            else:
                pass
        self._attributes = attr

    def get_parameters(self, parameters):
        """Converts parameters from Sympathy's format into a keyword dictionary
        suitable for sklearn"""
        kwargs = {}
        for name, info in self._parameters.items():
            type_ = info['type']
            skl_name = info['skl_name']

            if 'no-kw' in info and info['no-kw']:
                continue
            if 'deprecated' in info and info['deprecated']:
                if (name in parameters
                    and (type_.from_string(parameters[name].value) !=
                         type_.default)):

                    sywarn("Parameter {} is deprecated and will be ignored"
                           .format(name))
                continue

            value = type_.from_string(parameters[name].value)
            kwargs[skl_name] = value
        return kwargs

    @property
    def x_names(self):
        return self._x_names

    @x_names.setter
    def x_names(self, value):
        self._x_names = value

    def set_x_names(self, names):
        """Called by nodes that have access to the input name X"""
        self.x_names = names
        if self.mirror_xy_names:
            self._y_names = names

    @property
    def y_names(self):
        return self._y_names

    @y_names.setter
    def y_names(self, value):
        self._y_names = value

    def set_y_names(self, names):
        """
        Called by nodes that have access to the output name,
        usually this is Y
        """
        self.y_names = names
        if self.mirror_xy_names:
            self._x_names = names

    @property
    def xout_names(self):
        try:
            return self._xout_names
        except AttributeError:
            return self._y_names

    @xout_names.setter
    def xout_names(self, value):
        self._xout_names = value

    def set_mirroring(self):
        """Sets this descriptor to mirror x_names and y_names at all times"""
        self.mirror_xy_names = True

    def xnames_as_text(self):
        if self.x_names is None:
            return "unknown"
        else:
            text = self.x_names[0]
            for name in self.x_names[1:]:
                text += ", {0}".format(name)
            return text

    def ynames_as_text(self):
        if self.y_names is None:
            return "unknown"
        else:
            text = self.y_names[0]
            for name in self.y_names[1:]:
                text += ", {0}".format(name)
            return text

    def describe_skl(self, skl):
        text = "Capabilities: "
        caps = {sklearn.base.BaseEstimator: "Base Estimator",
                sklearn.base.TransformerMixin: "Transform",
                sklearn.base.ClassifierMixin: "Classifier",
                sklearn.base.ClusterMixin: "Clustering",
                sklearn.base.RegressorMixin: "Regressor"}
        order = [sklearn.base.BaseEstimator,
                 sklearn.base.ClassifierMixin,
                 sklearn.base.ClusterMixin,
                 sklearn.base.RegressorMixin,
                 sklearn.base.TransformerMixin]
        clss = inspect.getmro(skl.__class__)
        first = True
        for cls in order:
            if cls in clss:
                if not first:
                    text += ", "
                else:
                    first = False
                text += caps[cls]
        return text

    def post_fit(self, skl):
        pass

    def visualize(self, skl, layout):
        """
        Builds widget for visualizing the model. Default fallback using
        attributes
        """
        notebook = QtGui.QTabWidget()
        self.parameter_tab(skl, notebook)
        self.attribute_tabs(skl, notebook)
        layout.addWidget(notebook)

    def parameter_tab(self, skl, notebook):
        """Builds a tab containing parameters of model"""
        rows = 0 if skl is None else 1
        cols = len(self.descriptions)
        if cols == 0:
            return

        table_widget = QtGui.QTableWidget(rows, cols)
        table_widget.setToolTip("Lists all parameters and their "
                                "currently given value for the model")

        tbl = table.File()
        if skl is None:
            for name in self.parameters.keys():
                tbl.set_column_from_array(name, np.array([]))
        else:
            params = skl.get_params()
            for name in self.parameters.keys():
                if name in params:
                    type_ = self.types[name]
                    value = type_.to_string(params[name])
                    tbl.set_column_from_array(name, np.array([value]))
                else:
                    tbl.set_column_from_array(
                        name, np.ma.array([''], mask=[True]))

        viewer = TableViewer(table_=tbl, plot=False, show_title=False)
        viewer._data_preview._preview_table.setMinimumHeight(100)
        notebook.addTab(viewer, "Parameters")

    def attribute_tabs(self, skl, notebook):
        """Builds tabs for visualizing the attributes of the model."""

        attributes = self.attributes
        if len(attributes) == 0:
            return

        for attr_dict in attributes:
            name = attr_dict['name']
            try:
                value = self.get_attribute(skl, name)
            except AttributeError:
                continue
            except ValueError:
                continue

            cnames = None
            rnames = None
            if 'cnames' in attr_dict:
                cnames = attr_dict['cnames'](self, skl)
            if 'rnames' in attr_dict:
                rnames = attr_dict['rnames'](self, skl)
            doc = attr_dict['desc']

            tbls = value_to_tables(value, name, cnames=cnames, rnames=rnames)
            if len(tbls) == 0:
                continue
            elif len(tbls) == 1:
                viewer = TableViewer(
                    table_=tbls[0], plot=False, show_title=False)
                viewer._data_preview._preview_table.setMinimumHeight(100)
                viewer.setToolTip(doc)
            else:
                viewer = ListViewer(viewer_cls=TableViewer, data_list=tbls)
                viewer._row_changed(0)
                viewer.setToolTip(doc)
            notebook.addTab(viewer, name)
            notebook.setTabToolTip(notebook.count()-1, doc)

    def get_attribute(self, skl, attribute):
        return getattr(skl, attribute)

    def on_save(self, skl):
        """Called with object to be pickled before saving to disk"""
        return skl

    def on_load(self, skl):
        """Called with unpickled object after loaded from disk"""
        return skl

    def predict(self, skl, X):
        """
        Calls predict, or a similar function, on the given scikit learn object
        """
        return skl.predict(X)

    def transform(self, skl, X):
        """
        Calls transform, or a similar function, on the given skl object
        """
        return skl.transform(X)
