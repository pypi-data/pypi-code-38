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

from . import record as _record
from .meta import InlineMetaclassBase
from six import iteritems
from six.moves import zip

import types
import six


class Constructor(object):
  """
  Represents a constructor for a sumtype. Constructors are declared using
  record types (see the #record module) or by creating #Constructor objects
  from scratch (with the same interface as the #recor.create_record()
  function).

  This class is only used temporarily during the declaration of a sumtype
  and is then replaced by a #BoundConstructor.
  """

  def __init__(self, record_or_fields=(), *mixins):
    """
    Creates a new constructor object.

    # Arguments (1)

    record (type): A #record.CleanRecord subclass.

    # Arguments (2)

    fields (list, dict, str): Fields for the new record class.
    mixins (tuple of type): Mixins for the record subclass.
    """

    if isinstance(record_or_fields, type):
      if not issubclass(record_or_fields, _record.CleanRecord):
        raise TypeError('expected record.CleanRecord subclass')
      record = record_or_fields
    else:
      record = _record.create('_Temporary', record_or_fields, *mixins)
    self.record = record

  def add_member(self, name, value):
    setattr(self.record, name, value)

  def bind(self, name, sumtype):
    name = sumtype.__name__ + '.' + name
    attrs = {'__skip_sumtype_meta__': True}
    typ = type(name, (sumtype, self.record), attrs)
    typ.__constructor__ = self
    return typ


class member_of(object):
  """
  A decorator for functions or values that are supposed to be members of
  only a specific sumtype's constructor (or multiple constructors). Instances
  of this class will be automatically unpacked by the :class:`_SumtypeMeta`
  constructor and moved into the :attr:`Constructor.members` dictionary.
  """

  def __init__(self, constructors=None, value=None, name=None):
    if isinstance(constructors, Constructor):
      constructors = [constructors]
    if any(not isinstance(x, Constructor) for x in constructors):
      raise TypeError('expected only Constructor objects')
    self.constructors = constructors
    self.value = value
    self.name = name
    if self.name:
      self._propagate()

  def __call__(self, value):
    if self.name:
      raise RuntimeError('member_of.name already set')
    self.name = value.__name__
    self.value = value
    self._propagate()
    return self

  def _propagate(self):
    assert self.name
    for c in self.constructors:
      c.add_member(self.name, self.value)


class Sumtype(InlineMetaclassBase):
  """
  Base class for sumtypes.
  """

  __addins__ = []
  __constructors__ = {}

  def __metanew__(cls, name, bases, attrs):
    subtype = type.__new__(cls, name, bases, attrs)
    if attrs.get('__skip_sumtype_meta__', False):
      return subtype

    # Get all previous constructors and get all new ones.
    constructors = getattr(subtype, '__constructors__', {}).copy()
    for key, value in iteritems(vars(subtype)):
      if isinstance(value, Constructor):
        constructors[key] = value
      elif isinstance(value, type) and issubclass(value, _record.CleanRecord):
        constructors[key] = Constructor(value)

    # Update constructors from member_of declarations.
    for key, value in list(iteritems(vars(subtype))):
      if isinstance(value, member_of):
        delattr(subtype, key)

    # Bind constructors.
    for key, value in iteritems(constructors):
      setattr(subtype, key, value.bind(key, subtype))
    subtype.__constructors__ = constructors

    # Invoke addons.
    for addin in getattr(subtype, '__addins__', []):
      addin(subtype)

    return subtype


def add_is_methods(sumtype):
  """
  A sumtype add-in that adds an `is_...()` methods for every constructor.
  """

  import re

  def create_is_check(func_name, constructor_name):
    def check(self):
      return type(self) == getattr(self, constructor_name)
    check.__name__ = func_name
    check.__qualname__ = func_name
    return check

  for name in sumtype.__constructors__.keys():
    func_name = 'is_' + '_'.join(re.findall('[A-Z]+[^A-Z]*', name)).lower()
    setattr(sumtype, func_name, create_is_check(func_name, name))


Sumtype.constructor = Constructor
Sumtype.member_of = member_of
Sumtype.add_is_methods = add_is_methods
Sumtype.__addins__.append(add_is_methods)

import sys
Sumtype.__module_object__ = sys.modules[__name__]  # keep explicit reference for Py2
sys.modules[__name__] = Sumtype
