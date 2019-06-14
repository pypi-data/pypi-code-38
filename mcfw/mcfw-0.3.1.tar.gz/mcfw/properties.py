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

import hashlib
import inspect
import pprint
from types import NoneType

import sys

from consts import MISSING

try:
    from google.appengine.ext import ndb

    GAE = True
except ImportError:
    GAE = False  # Allow running outside app engine


def rich_str(obj):
    if GAE:
        if isinstance(obj, ndb.Model):
            d = obj.to_dict()
            d['__class__'] = obj.__class__
            for big_data_attr in ('blob', 'picture', 'avatar'):
                if big_data_attr in d:
                    del d[big_data_attr]
            return pprint.pformat(d)
    if isinstance(obj, (dict, list)):
        return pprint.pformat(obj)
    if isinstance(obj, str):
        return obj
    else:
        return unicode(obj).encode('utf8')


def azzert(condition, error_message=''):
    if not condition:
        raise AssertionError(reduce(lambda remainder, item: remainder + '\n  - ' + item[0] + ': ' + rich_str(item[1]),
                                    sorted(sys._getframe(1).f_locals.iteritems()), str(error_message) + '\n  Locals: '))


simple_types = (int, long, str, unicode, bool, float, NoneType)
__none__ = '__none__'


class object_factory(object):

    def __init__(self, subtype_attr_name, subtype_mapping):
        self.subtype_attr_name = subtype_attr_name
        self.subtype_mapping = subtype_mapping

    def get_subtype(self, instance):
        if instance is MISSING or instance is None:
            return self
        if isinstance(instance, dict):
            subtype_name = instance.get(self.subtype_attr_name)
        else:
            subtype_name = getattr(instance, self.subtype_attr_name, None)

        if subtype_name is None:
            raise ValueError('%s instance has no or empty attribute \'%s\'' % (type(instance), self.subtype_attr_name))

        subtype = self.subtype_mapping.get(subtype_name, None)
        if subtype is None:
            raise ValueError('\'%s\' not found in %s' % (subtype_name, self.subtype_mapping))

        return subtype


class typed_property(object):

    def __init__(self, name, type_, list_=False, doc=None, subtype_attr_name=None, subtype_mapping=None,
                 default=MISSING, hash_serializer=str):
        self.type = type_
        self.list = list_
        self.attr_name = u'_%s' % name
        self.doc = doc
        self.hash_serializer = hash_serializer
        azzert((subtype_attr_name and subtype_mapping) or (not subtype_mapping and not subtype_attr_name),
               'supply both subtype_attr_name and subtype_mapping')
        azzert(not (list_ and (subtype_attr_name or subtype_mapping)),
               'subtype_mapping is not supported in combination with lists')
        self.subtype_attr_name = subtype_attr_name
        self.subtype_mapping = subtype_mapping
        if default is not MISSING:
            if list_:
                azzert(hasattr(default, '__iter__') and len(default) == 0,
                       'Only empty list allowed as default value for list properties')
            if default is None:
                azzert(self.type not in ('bool', 'int', 'long', 'float'),
                       'None not allowed for %s properties' % self.type)

        self.default = default
        self.__name__ = name

    def __doc__(self):
        return self.doc

    def __get__(self, instance, owner):
        if not instance:
            return self
        else:
            return getattr(instance, self.attr_name, self.default)

    def __set__(self, instance, value):
        if value is not MISSING:
            if self.list:
                if not isinstance(value, (list, tuple, set)):
                    raise ValueError(
                        'Expected [%s] for \'%s\' and got %s - %s!' % (self.type, self.attr_name, type(value), value))
                for i, x in enumerate(value):
                    if self._is_invalid_type(x, instance):
                        raise ValueError('Not all items are from expected type %s! Encountered item at index %s with '
                                         'type %s.' % (unicode(self.type), i, type(x)))
            else:
                if self._is_invalid_type(value, instance):
                    raise ValueError(
                        'Expected %s for \'%s\' and got %s - %s!' % (self.type, self.attr_name, type(value), value))
        setattr(instance, self.attr_name, value)

    def _is_invalid_type(self, value, instance):
        type_ = self.type.get_subtype(value) if isinstance(self.type, object_factory) else self.type
        if value and not isinstance(value, type_):
            return True

        if self.subtype_attr_name and self.subtype_mapping:
            subtype = self.get_subtype(instance)

            if value and not isinstance(value, subtype):
                raise ValueError('Expected %s and got %s - %s!' % (subtype, type(value), value))

        return False

    def get_subtype(self, instance):
        subtype_name = getattr(instance, self.subtype_attr_name, None)
        if subtype_name is None:
            raise ValueError('%s instance has no or empty attribute \'%s\'' % (type(instance), self.subtype_attr_name))

        subtype = self.subtype_mapping.get(subtype_name, None)
        if subtype is None:
            raise ValueError('\'%s\' not found in %s' % (subtype_name, self.subtype_mapping))

        return subtype


unicode_property = unicode_list_property = None
bool_property = bool_list_property = None
long_property = long_list_property = None
float_property = float_list_property = None

_this_mod = locals()


def _generate_properties():
    for type_, list_, name, hash_serializer in (
            (unicode, True, 'unicode_list_property', lambda x: __none__ if x is None else x.encode('utf8')),
            ((int, long), False, 'long_property', str),
            ((int, long), True, 'long_list_property', str),
            ((float, int), False, 'float_property', str),
            ((float, int), True, 'float_list_property', str),
            (bool, False, 'bool_property', str),
            (bool, True, 'bool_list_property', str)):
        def wrap(t, l):
            def init(self, name, doc=None, default=MISSING, hash_serializer=hash_serializer):
                typed_property.__init__(self, name, t, l, doc, default=default, hash_serializer=hash_serializer)

            return init

        _this_mod[name] = type(name, (typed_property,), {'__init__': wrap(type_, list_)})


_generate_properties()
del _generate_properties
del _this_mod


class unicode_property(typed_property):

    def __init__(self, name, doc=None, empty_string_is_null=False, default=MISSING):
        typed_property.__init__(self, name, unicode, False, doc, default=default,
                                hash_serializer=lambda x: __none__ if x is None else x.encode('utf8'))
        self._empty_string_is_null = empty_string_is_null

    def __get__(self, instance, owner):
        value = typed_property.__get__(self, instance, owner)
        return None if self._empty_string_is_null and isinstance(value, unicode) and value == u'' else value


simple_property_types = [unicode_property, unicode_list_property, float_property, float_list_property,
                         bool_property, bool_list_property, long_property, long_list_property]

_members_cache = {}


def get_members(type_):
    if type_ in _members_cache:
        return _members_cache[type_]
    else:
        members = sorted(inspect.getmembers(type_, lambda value: isinstance(value, typed_property)), key=lambda x: x[0])
        simple_members = filter(lambda (name, prop): type(prop) in simple_property_types, members)
        complex_members = filter(lambda x: x not in simple_members, members)
        _members_cache[type_] = (complex_members, simple_members)
        return complex_members, simple_members


def get_hash(object_):
    def feed(digester, object_):
        if object_ is None:
            digester.update(__none__)
        cms, sms = get_members(type(object_))
        for name, prop in cms:
            value = getattr(object_, name)
            if prop.list:
                for val in value:
                    feed(digester, val)
            else:
                feed(digester, value)
        for name, prop in sms:
            value = getattr(object_, name)
            if value is None:
                digester.update(__none__)
                continue
            if prop.list:
                for val in value:
                    digester.update(prop.hash_serializer(val))
            else:
                digester.update(prop.hash_serializer(value))

    digester = hashlib.md5()
    feed(digester, object_)
    return digester.hexdigest()
