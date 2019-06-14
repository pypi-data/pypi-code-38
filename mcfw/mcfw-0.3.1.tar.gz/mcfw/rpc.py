# -*- coding: utf-8 -*-
# Copyright 2018 Mobicage NV
# NOTICE: THIS FILE HAS BEEN MODIFIED BY MOBICAGE NV IN ACCORDANCE WITH THE APACHE LICENSE VERSION 2.0
# Copyright 2018 GIG Technology NV
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
# @@license_version:1.5@@

import inspect
import logging
import types
from types import NoneType

import itertools
from google.appengine.ext import ndb

from mcfw.cache import set_cache_key
from mcfw.consts import MISSING
from mcfw.properties import get_members, simple_types, object_factory, long_property, unicode_property, typed_property


class ErrorResponse(object):
    status_code = long_property('1')
    error = unicode_property('2')
    data = typed_property('3', dict)

    def __init__(self, rest_exception):
        """
        Args:
            rest_exception (mcfw.exceptions.HttpException):
        """
        self.status_code = rest_exception.http_code
        self.error = u'%s' % rest_exception.error
        self.data = rest_exception.data


class MissingArgumentException(Exception):

    def __init__(self, name, func=None):
        Exception.__init__(self, '%s is a required argument%s!' % (
            name, (' in function %s' % func.func_name) if func else ''))
        self.name = name


def arguments(**kwarg_types):
    """ The arguments decorator function describes & validates the parameters of the function."""
    for value in kwarg_types.itervalues():
        _validate_type_spec(value)

    def wrap(f):
        # validate argspec
        f_args = inspect.getargspec(f)
        f_args = inspect.ArgSpec([a for a in f_args[0] if a not in ('self', 'cls')], f_args[1], f_args[2], f_args[3])
        f_arg_count = len(f_args[0])
        f_defaults = f_args[3]
        if not f_defaults:
            f_defaults = []
        f_arg_defaults_count = len(f_defaults)
        f_arg_no_defaults_count = f_arg_count - f_arg_defaults_count
        f_arg_defaults = {
            f_args[0][i]: f_defaults[i - f_arg_no_defaults_count] if i >= f_arg_no_defaults_count else MISSING
            for i in xrange(f_arg_count)}
        f_pure_default_args_dict = {f_args[0][i]: f_defaults[i - f_arg_no_defaults_count]
                                    for i in xrange(f_arg_no_defaults_count, f_arg_count)}
        if f_arg_count != len(kwarg_types):
            raise ValueError(f.func_name + ' does not contain the expected arguments!')
        unknown_args = [arg for arg in f_args[0] if arg not in kwarg_types]
        if unknown_args:
            raise ValueError('No type information is supplied for %s!' % ', '.join(unknown_args))

        def typechecked_f(*args, **kwargs):
            arg_length = len(args)
            if arg_length > f_arg_count:
                raise ValueError('%s() takes %s arguments (%s given)' % (f.__name__, f_arg_count, arg_length))

            for i in xrange(arg_length):
                kwargs[f_args[0][i]] = args[i]

            # accept MISSING as magical value or not
            accept_missing = 'accept_missing' in kwargs
            if accept_missing:
                kwargs.pop('accept_missing')
            # apply default value if available
            for arg in kwarg_types:
                value = kwargs.get(arg, f_arg_defaults[arg])
                if value is MISSING:
                    value = f_arg_defaults.get(arg, MISSING)
                kwargs[arg] = value
            # validate number of arguments
            if not len(kwargs) == len(kwarg_types):
                raise ValueError('kwarg mismatch\nExpected:%s\nGot:%s' % (kwarg_types, kwargs))
            # validate supplied arguments
            unknown_args = [arg for arg in kwargs if arg not in kwarg_types]
            if unknown_args:
                raise ValueError('Unknown argument(s) %s supplied!' % ', '.join(unknown_args))
            # validate argument values
            for arg in kwargs:
                _check_type(arg, kwarg_types[arg], kwargs[arg], accept_missing=accept_missing, func=f)
            return f(**kwargs)

        set_cache_key(typechecked_f, f)
        typechecked_f.__name__ = f.__name__
        typechecked_f.__module__ = f.__module__
        typechecked_f.meta['fargs'] = f_args
        typechecked_f.meta['kwarg_types'] = kwarg_types
        typechecked_f.meta['pure_default_args_dict'] = f_pure_default_args_dict
        if hasattr(f, 'meta'):
            typechecked_f.meta.update(f.meta)

        return typechecked_f

    return wrap


def returns(type_=NoneType):
    """ The returns decorator function describes & validates the result of the function."""
    _validate_type_spec(type_)

    def wrap(f):
        def typechecked_return(*args, **kwargs):
            result = f(*args, **kwargs)
            return _check_type(u'Result', type_, result, func=f)

        set_cache_key(typechecked_return, f)
        typechecked_return.__name__ = f.__name__
        typechecked_return.__module__ = f.__module__
        typechecked_return.meta[u'return_type'] = type_
        if hasattr(f, u'meta'):
            typechecked_return.meta.update(f.meta)
        return typechecked_return

    return wrap


def run(function, args, kwargs):
    kwargs['accept_missing'] = None
    result = function(*args, **kwargs)
    type_, islist = _get_return_type_details(function)
    return serialize_value(result, type_, islist, skip_missing=True)


def parse_parameters(function, parameters):
    kwarg_types = get_parameter_types(function)
    return get_parameters(parameters, kwarg_types)


def parse_complex_value(type_, value, islist):
    if value is None:
        return None
    if isinstance(type_, tuple):
        if islist:
            return [_parse_value(None, type_, val) for val in value]
        else:
            return _parse_value(None, type_, value)
    else:
        parser = _get_complex_parser(type_)
        if islist:
            return map(parser, value)
        else:
            return parser(value)


def check_function_metadata(function):
    if 'kwarg_types' not in function.meta or 'return_type' not in function.meta:
        raise ValueError('Can not execute function. Too little meta information is available!')


def get_parameter_types(function):
    return function.meta['kwarg_types']


def get_parameters(parameters, kwarg_types):
    return {name: parse_parameter(name, type_, parameters[name]) if name in parameters else MISSING
            for name, type_ in kwarg_types.iteritems()}


def get_type_details(type_, value=MISSING):
    if isinstance(type_, tuple):
        # The value can have multiple types.
        if value is not MISSING:
            # We must find the type by comparing the possible types with the real type of <value>
            value_is_list = isinstance(value, list)
            if value_is_list:
                if not value:
                    return unicode, True  # The type doesn't matter, the list is empty
                value = value[0]
            for t in type_:
                is_list = isinstance(t, list)
                if is_list != value_is_list:
                    continue
                if is_list:
                    t = t[0]
                if t in (str, unicode):
                    type_to_check = (str, unicode)
                elif t in (int, long):
                    type_to_check = (int, long)
                else:
                    type_to_check = t
                if isinstance(value, type_to_check):
                    return type(value), is_list
                    # Weird... type not found and @arguments didn't raise... The serialization will probably fail.

    is_list = isinstance(type_, list)
    if is_list:
        type_ = type_[0]
    return type_, is_list


def serialize_complex_value(value, type_, islist, skip_missing=False):
    if type_ == dict:
        return value

    def optimal_serializer(val):
        if isinstance(type_, tuple):
            for type_option in type_:
                if isinstance(val, type_option):
                    def serializer(value, skip_missing):
                        return serialize_value(value, type_option, False, skip_missing)
                    break
            else:
                raise ValueError("Could not map val to a type in %s" % type_)
        elif not isinstance(type_, object_factory) and isinstance(val, type_):
            serializer = _get_complex_serializer(val.__class__)
        else:
            serializer = _get_complex_serializer(type_)
        return serializer(val, skip_missing)

    if value is None:
        return None
    if islist:
        try:
            return map(optimal_serializer, value)
        except Exception:
            logging.warn('value for type %s was %s', type_, value)
            raise
    else:
        return optimal_serializer(value)


def serialize_value(value, type_, islist, skip_missing=False):
    if value is None or type_ in simple_types or (isinstance(type_, tuple) and all(t in simple_types for t in type_)):
        return value
    else:
        return serialize_complex_value(value, type_, islist, skip_missing)


def parse_parameter(name, type_, value):
    raw_type, is_list = get_type_details(type_, value)
    if isinstance(value, list) != is_list:
        raise ValueError('list expected for parameter %s and got %s or vice versa!' % (name, value))
    if isinstance(value, list):
        return map(lambda x: _parse_value(name, raw_type, x), value)
    else:
        return _parse_value(name, raw_type, value)


def _validate_type_spec(type_):
    if isinstance(type_, list) and len(type_) != 1:
        raise ValueError('Illegal type specification!')


DICT_KEY_ITERATOR_TYPE = type({}.iterkeys())


def _check_type(name, type_, value, accept_missing=False, func=None):
    if value is MISSING:
        if accept_missing:
            return value
        else:
            raise MissingArgumentException(name, func)

    checktype = (str, unicode) if type_ in (str, unicode) else type_
    checktype = (int, long) if checktype in (int, long) else checktype
    if value is None and (isinstance(checktype, list) or type_ not in (int, long, float, bool)):
        return value

    if isinstance(type_, tuple):
        # multiple types are allowed. checking if value is one of the them.
        errors = []
        for t in type_:
            try:
                return _check_type(name, t, value, accept_missing, func)
            except (ValueError, TypeError) as e:
                errors.append(e)
                continue
        logging.debug('\n\n'.join(map(str, errors)))
        raise ValueError('%s is not of expected type %s! Its type is %s:\n%s' % (name, str(type_), type(value), value))

    if isinstance(checktype, list) and isinstance(value, list):
        checktype = (str, unicode) if checktype[0] in (str, unicode) else checktype[0]

        for i, x in enumerate(value):
            t = checktype.get_subtype(x) if isinstance(checktype, object_factory) else checktype
            if not isinstance(x, t):
                raise ValueError(
                    '%s: Not all items were of expected type %s. Encountered an item at index %s with type %s: %s.'
                    % (name, str(checktype), i, type(x), x))
    elif isinstance(checktype, list) and isinstance(value, (types.GeneratorType, ndb.Query, itertools.chain,
                                                            DICT_KEY_ITERATOR_TYPE)):
        checktype = (str, unicode) if checktype[0] in (str, unicode) else checktype[0]

        def checkStreaming():
            for o in value:
                if not isinstance(o, checktype):
                    raise ValueError('%s: Not all items were of expected type %s' % (name, str(checktype)))
                yield o

        return checkStreaming()
    elif checktype == type and isinstance(value, list):
        if len(value) != 1:
            raise ValueError('%s: unexpected type count (%s)' % (name, len(value)))

        def check(t, i):
            if not isinstance(t, type):
                raise ValueError(
                    '%s: Not all items were of expected type %s. Encountered an item at index %s with type %s: %s.'
                    % (name, str(checktype), i, type(x), x))

        if isinstance(value[0], tuple):
            for i, t in enumerate(value[0]):
                check(t, i)
        else:
            check(value[0], 0)
    else:
        if isinstance(checktype, object_factory):
            checktype = checktype.get_subtype(value)
        try:
            if not isinstance(value, checktype):
                raise ValueError(
                    '%s is not of expected type %s! Its type is %s:\n%s' % (name, str(checktype), type(value), value))
        except TypeError as e:
            raise TypeError('%s\nvalue: %s\nchecktype: %s' % (e.message, value, checktype))
    return value


_complexParserCache = {}


def _get_complex_parser(type_):
    if type_ is dict:
        return lambda x: x
    if type_ not in _complexParserCache:
        def parse(value):
            t = type_.get_subtype(value) if isinstance(type_, object_factory) else type_
            inst = t()

            complex_members, simple_members = get_members(t)
            for name, prop in simple_members:
                setattr(inst, name, value[name] if name in value else getattr(t, name).default)
            for name, prop in complex_members:
                setattr(inst, name, parse_complex_value(
                    prop.get_subtype(inst) if (prop.subtype_attr_name and prop.subtype_mapping) else prop.type,
                    value[name], prop.list) if name in value else MISSING)
            return inst

        _complexParserCache[type_] = parse
        return parse
    else:
        return _complexParserCache[type_]


_value_types = {int, long, float, bool, NoneType}


def _parse_value(name, type_, value):
    def raize():
        if name:
            raise ValueError('Incorrect type received for parameter \'%s\'. Expected %s and got %s (%s).'
                             % (name, type_, type(value), value))
        else:
            raise ValueError('Could not parse %s as %s' % (value, type_))
    istuple = isinstance(type_, tuple)
    if (istuple and set(type_).issubset(_value_types)) or type_ in _value_types:
        if not isinstance(value, type_):
            raize()
        return value
    elif istuple:
        for tt in type_:
            try:
                return _parse_value(name, tt, value)
            except ValueError:
                pass
        raize()
    elif value is None:
        return None
    elif type_ == unicode:
        if not isinstance(value, (str, unicode)):
            raize()
        return value if isinstance(value, unicode) else unicode(value)
    elif type_ == str:
        if not isinstance(value, (str, unicode)):
            raize()
        return value
    elif not isinstance(value, dict):
        raize()
    return parse_complex_value(type_, value, False)


_complex_serializer_cache = {}


def _get_complex_serializer(type_):
    if type_ not in _complex_serializer_cache:
        def serializer(value, skip_missing):
            t = type_.get_subtype(value) if isinstance(type_, object_factory) else type_
            complex_members, simple_members = get_members(t)

            result = {name: getattr(value, name) for (name, _) in simple_members
                      if not skip_missing or getattr(value, name) is not MISSING}

            def _serialize(name, prop):
                attr = getattr(value, name)
                real_type = prop.get_subtype(value) if (prop.subtype_attr_name and prop.subtype_mapping) else prop.type
                serialized_value = serialize_complex_value(attr, real_type, prop.list, skip_missing)
                return serialized_value

            result.update({name: _serialize(name, prop) for (name, prop) in complex_members
                           if not skip_missing or getattr(value, name) is not MISSING})

            return result

        _complex_serializer_cache[type_] = serializer
        return serializer
    else:
        return _complex_serializer_cache[type_]


def _get_return_type_details(function):
    return get_type_details(function.meta['return_type'])
