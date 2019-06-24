# -*- coding: utf8 -*-
# Copyright (c) 2019 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

__all__ = ['Field', 'CleanRecord', 'Record', 'create_record']

from . import NotSet, abc
from .maps import OrderedDict
from .meta import InlineMetaclassBase
from six import iteritems, itervalues

import inspect
import six
import sys
import types


class Field(object):
  """
  Represents a field of a #Record class. Fields have a name, type and
  a default value. If a field has no name, it is "unbound" and the name
  may be derived from the name the field was assigned to in the #Record
  subclass declaration.
  """

  _global_create_index = 0

  def __init__(self, type, default=NotSet):
    self.name = None
    self.type = type
    self.default = default
    self.create_index = Field._global_create_index
    Field._global_create_index += 1

  def __repr__(self):
    return 'Field(name={!r}, type={!r}, default={!r})'.format(
      self.name, self.type, self.default)

  def get_default(self):
    if self.default is NotSet:
      raise RuntimeError('Field.default is NotSet')
    if isinstance(self.default, types.LambdaType):
      return self.default()
    return self.default

  @classmethod
  def with_name(cls, name, *args, **kwargs):
    obj = cls(*args, **kwargs)
    obj.name = name
    return obj


def compile_fields(decl, field_type):
  """
  Compiles a fields declaration to an #OrderedDict mapping to #Field objects.
  A fields declaration can be a string, list or dictionary.

  For a string: Comma or whitespace separated.

  For a list:

  * Field
  * Tuple[str, Type] (name, type)
  * Tuple[str, Type, Union[LambdaType, Any]] (name, type, default)

  For a dictionary:

  * Field
  * Tuple[Type, Union[LambdaType, Any]] (type, default)
  * Type
  """

  is_ordered = True

  # Split string into list of field names.
  if isinstance(decl, str):
    decl = [x.strip() for x in decl.split(',' if ',' in decl else ' ')]

  # Convert a mapping to the list form.
  elif isinstance(decl, abc.Mapping):
    is_ordered = False
    new_decl = []
    for key, value in iteritems(decl):
      if isinstance(value, tuple):
        value = (key,) + value
      elif isinstance(value, Field):
        value.name = key
      else:
        value = (key, value)
      new_decl.append(value)
    decl = new_decl

  compiled_fields = OrderedDict()
  for item in decl:
    if isinstance(item, str):
      field = field_type.with_name(item, None, NotSet)
    elif isinstance(item, field_type):
      field = item
    elif isinstance(item, tuple):
      if len(item) == 1:
        name, type_, default = item[0], None, NotSet
      elif len(item) == 2:
        name, type_, default = item[0], item[1], NotSet
      elif len(item) == 3:
        name, type_, default = item
      else:
        raise ValueError('invalid tuple Field declaration: {!r}'.format(item))
      field = field_type.with_name(name, type_, default)
    elif isinstance(item, dict):
      field = field_type.with_name(**item)
    else:
      raise TypeError('unexpected Field declaration: {!r}'.format(item))
    if not field.name:
      raise ValueError('unbound Field found: {!r}'.format(field.name))
    if field.name in compiled_fields:
      raise ValueError('duplicate Field name: {!r}'.format(field.name))
    compiled_fields[field.name] = field

  if not is_ordered:
    ordered = sorted(compiled_fields.items(), key=lambda x: x[1].create_index)
    compiled_fields = OrderedDict(ordered)

  return compiled_fields


class CleanRecord(InlineMetaclassBase):
  """
  A base-class similar to #typing.NamedTuple, but mutable. Fields can be
  specified using Python 3.6 class-member annotations, by setting the
  `__annotations__` or `__fields__` member to a list of annotations or
  by declaring class-members as #Field objects.

  In the following example all four `Person` declarations are identical.

  ```python
  class Person(Record):
    mail: str
    name: str = lambda: random_name()
    age: int = 0

  class Persom(Record):
    __fields__ = [
      ('mail', str),
      ('name', str, lambda: random_name()),
      ('age', int, 0)
    ]

  class Person(Record):
    mail = Field(str)
    name = Field(str, lambda: random_name())
    age = Field(str, 0)

  Person = create_record('Person', [
    ('mail', str),
    Field.with_name('name', str, lambda: random_name()),
    ('age', int, 0)
  ])
  ```
  """

  __field_type__ = Field

  def __metainit__(self, name, bases, dict):
    """
    Overrides #InlineMetaclassBase.__metainit__(). Converts the fields or
    annotations defined on the class to a common dictionary representation.
    The source of the fields is determined in the following order:

    * Attribute `__fields__`
    * Attribute `__annotations__`
    * Member attributes (only #Field instances)
    """

    field_type = self.__field_type__

    # Determine the source for the field declaration.
    if '__fields__' in dict:
      fields = dict['__fields__']
    elif '__annotations__' in dict:
      fields = dict['__annotations__']
      if isinstance(fields, abc.Mapping):
        for key, value in iteritems(fields):
          fields[key] = (value, getattr(self, key, NotSet))
    else:
      fields = []
      for key, value in iteritems(dict):
        if isinstance(value, field_type):
          if value.name is None:
            value.name = key
          elif value.name != key:
            raise ValueError('Field.name mismatches key: {!r} != {!r}'
              .format(value.name, key))
          fields.append(value)
      fields.sort(key=lambda x: x.create_index)

    # Merge with parent class fields.
    mro_fields = OrderedDict()
    for base in reversed(bases):
      if hasattr(base, '__fields__'):
        mro_fields.update(base.__fields__)
    mro_fields.update(compile_fields(fields, field_type))

    for name, field in iteritems(mro_fields):
      if name != field.name:
        raise ValueError('mismatching Field name: name({!r}) != Field.name({!r})'
          .format(name, field.name))

    self.__fields__ = mro_fields

  def __init__(self, *args, **kwargs):
    type_name = type(self).__name__

    # Validate number of arguments.
    nargs = len(args) + len(kwargs)
    if nargs > len(self.__fields__):
      raise TypeError('{}() expected at most {} arguments, got {}'
        .format(type_name, len(self.__fields__), nargs))

    # Raise an exception for any unknown keyword arguments.
    for key in kwargs:
      if key not in self.__fields__:
        raise TypeError('{}() unexpected keyword argument "{}"'
          .format(type_name, key))

    # Map positional arguments to keyword arguments.
    for arg, (key, field) in zip(args, iteritems(self.__fields__)):
      if field.name in kwargs:
        raise TypeError('{}() got duplicate argument "{}"'
          .format(type_name, name))
      kwargs[field.name] = arg

    # Create attributes.
    for key, field in iteritems(self.__fields__):
      value = kwargs.get(key, NotSet)
      if value is NotSet:
        if field.default is NotSet:
          raise TypeError('{}() missing argument "{}"'.format(type_name, key))
        value = field.get_default()
      setattr(self, key, value)

  def __repr__(self):
    values = ((k, getattr(self, k)) for k in self.__fields__)
    members = ', '.join('{}={!r}'.format(k, v) for k, v in values)
    return '{}({})'.format(type(self).__name__, members)

  def __eq__(self, other):
    if isinstance(other, CleanRecord) and self.__fields__ is other.__fields__:
      for key in self.__fields__:
        if getattr(self, key) != getattr(other, key):
          return False
      return True
    return False


class ToJSON(object):
  """
  A mixin for the #CleanRecord class that adds a #to_json() method.
  Different from the #as_dict() method in the #AsDict mixin, #to_json()
  is called recursively on any of the attributes if they have a #to_json()
  method.
  """

  def to_json(self):
    """
    Converts the record to a representation that can be dumped into JSON
    format. For any member, it will check if that member has a `to_json()`
    method and call it. Mappings and sequences are converted recursively.

    Note that this method does not guarantee that the returned object will
    be JSON serializable afterwards. For special cases, the method should
    be overwritten.
    """

    def coerce(value):
      if hasattr(value, 'to_json'):
        return value.to_json()
      elif isinstance(value, abc.Mapping):
        return dict((k, value[k]) for k in value)
      elif isinstance(value, abc.Sequence) and not isinstance(value, (six.string_types, six.binary_type, bytearray)):
        return [coerce(x) for x in value]
      else:
        return value

    result = {}
    for key in self.__fields__:
      result[key] = coerce(getattr(self, key))
    return result


class AsDict(object):
  """
  A mixin for the #CleanRecord class that adds an #as_dict() method.
  """

  def as_dict(self):
    return dict((k, getattr(self, k)) for k in self.__fields__)


class Sequence(object):
  """
  A mixin for the #CleanRecord class that implements the mutable sequence
  interface.
  """

  def __iter__(self):
    for key in self.__fields__:
      yield getattr(self, key)

  def __len__(self):
    return len(self.__fields__)

  def __getitem__(self, index):
    if hasattr(index, '__index__'):
      return getattr(self, self.__fields__[index.__index__()].name)
    elif isinstance(index, str):
      return getattr(self, str)
    else:
      raise TypeError('cannot index with {} object'
        .format(type(index).__name__))

  def __setitem__(self, index, value):
    if hasattr(index, '__index__'):
      setattr(self, self.__fields__[index.__index__()].name, value)
    elif isinstance(index, str):
      setattr(self, index, value)
    else:
      raise TypeError('cannot index with {} object'
        .format(type(index).__name__))


class Record(CleanRecord, ToJSON, AsDict):
  pass


def _get_calling_module_name(_stackdepth=0):
  frame = sys._getframe(_stackdepth+2)
  return frame.f_globals.get('__name__', __name__)


def create_record(name, fields, *mixins, **kwargs):
  """
  Creates a new #Record subclass. If at least one *mixin* is specified, it is
  mixed into the parent class of the created #Record subclass. One of the
  mixins can also be a separate #Record subclass in which case it is used
  as the parent class instead of #Record.
  """

  module = kwargs.pop('module', None)
  if module is None:
    module = _get_calling_module_name()

  for key in kwargs:
    raise TypeError('unexpected keyword argument: {!r}'.format(key))

  base = next((x for x in mixins if issubclass(x, CleanRecord)), None)
  if not base:
    mixins = mixins + (Record,)

  return type(name, mixins, {'__fields__': fields, '__module__': module})


def clone_record(record_cls, name=None, module=None):
  """
  Creates a clone of the specified *record_cls*. Optionally overrides the
  new classes *name*.
  """

  if module is None:
    module = _get_calling_module_name()

  assert isinstance(record_cls, type), record_cls
  assert issubclass(record_cls, CleanRecord), record_cls

  name = name or record_cls.__name__
  return create_record(name, record_cls.__fields__, *record_cls.__bases__,
    module=module)


create = create_record


from . import moduletools as _moduletools
_moduletools.make_inheritable(__name__, Record)
