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

import sys
import types

from .  import NotSet


class _InheritableModuleTypeClass(type):
  """
  A meta-class to create a class that can be inherited from to actually
  inherit from the `__inheritable_type__`, and redirect attribute access
  to the `__wrapped__` module.
  """

  def __new__(cls, name, bases, attrs):
    if bases == (types.ModuleType,):
      return type.__new__(cls, name, bases, attrs)
    new_bases = []
    inheritable_type = NotSet
    for base in bases:
      if isinstance(base, _InheritableModuleTypeClass):
        inheritable_type = base.__inheritable_type__
      else:
        new_bases.append(base)
    if inheritable_type is NotSet:
      raise RuntimeError('__inheritable_type__ not set')
    return type(name, (inheritable_type,) + tuple(new_bases), attrs)

  def __init__(self, name, bases, attrs):
    super(_InheritableModuleTypeClass, self).__init__(name, bases, attrs)
    assert '__wrapped__' in attrs
    assert '__inheritable_type__' in attrs

  def __getattr__(self, key):
    return getattr(self.__wrapped__, key)

  def __setattr__(self, key, value):
    return setattr(self.__wrapped__, key, value)


class _ProxyModuleType(types.ModuleType):

  def __init__(self, name, file, path, wrapped):
    super(_ProxyModuleType, self).__init__(name)
    types.ModuleType.__setattr__(self, '__file__', file)
    if path is not None:
      types.ModuleType.__setattr__(self, '__path__', path)
    types.ModuleType.__setattr__(self, '__wrapped__', wrapped)

  def __getattr__(self, key):
    return getattr(self.__wrapped__, key)

  def __setattr__(self, key, value):
    return setattr(self.__wrapped__, key, value)


class _CallableModuleType(_ProxyModuleType):

  def __init__(self, name, file, path, wrapped, call_target):
    super(_CallableModuleType, self).__init__(name, file, path, wrapped)
    self.__call_target__ = call_target

  def __call__(self, *args, **kwargs):
    return self.__call_target__(*args, **kwargs)


def make_inheritable(module_name, inheritable_type):
  """
  Makes the module with the specified *module_name* inheritable to the
  specified *inheritable_type*.
  """

  sys.modules[module_name] = _InheritableModuleTypeClass(
    module_name,
    (types.ModuleType,),
    {'__wrapped__': sys.modules[module_name], '__inheritable_type__': inheritable_type})


def make_callable(module_name, target):
  """
  Makes the module with the specified *module_name* callable with *target*.
  """

  module = sys.modules[module_name]
  sys.modules[module_name] = _CallableModuleType(
    module_name,
    module.__file__,
    getattr(module, '__path__', None),
    module,
    target)
