#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Computed attributes based on schema fields.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports
import sys

from Acquisition import aq_base
from Acquisition.interfaces import IAcquirer
from zope.schema import interfaces as sch_interfaces
from zope.schema.fieldproperty import FieldProperty
from zope.schema.fieldproperty import FieldPropertyStoredThroughField
from zope.schema.fieldproperty import createFieldProperties

__docformat__ = "restructuredtext en"

class AcquisitionFieldProperty(FieldProperty):
    """
    A field property that supports acquisition. Returned objects
    will be ``__of__`` the instance, and set objects will always be the unwrapped
    base.
    """

    def __get__(self, instance, klass):
        result = super(AcquisitionFieldProperty, self).__get__(instance, klass)
        if instance is not None and IAcquirer.providedBy(result):  # even defaults get wrapped
            result = result.__of__(instance)
        return result

    def __set__(self, instance, value):
        super(AcquisitionFieldProperty, self).__set__(instance, aq_base(value))

class UnicodeConvertingFieldProperty(FieldProperty):
    """
    Accepts bytes input for the unicode property if it can be
    decoded as UTF-8. This is primarily to support legacy test cases
    and should be removed when all constants are unicode.
    """

    def __set__(self, inst, value):
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        super(UnicodeConvertingFieldProperty, self).__set__(inst, value)

def _find_schema_from_field(field):
    if not sch_interfaces.IObject.providedBy(field) and not hasattr(field, 'schema'):
        raise sch_interfaces.WrongType("Don't know how to get schema from %s" % field)
    return field.schema

def _make_adapter_set(klass):

    def __set__(self, inst, value):
        try:
            super(klass, self).__set__(inst, value)
        except sch_interfaces.SchemaNotProvided:
            try:
                value = self.schema(value)
            except TypeError:
                # Let's raise the better error when we call again
                pass

            super(klass, self).__set__(inst, value)

    return __set__

class AdaptingFieldProperty(FieldProperty):
    """
    Primarily for legacy support and testing, adds adaptation to an interface
    when setting a field. This is most useful when the values are simple literals
    like strings.
    """

    def __init__(self, field, name=None):
        self.schema = _find_schema_from_field(field)
        super(AdaptingFieldProperty, self).__init__(field, name=name)

AdaptingFieldProperty.__set__ = _make_adapter_set(AdaptingFieldProperty)

class AdaptingFieldPropertyStoredThroughField(FieldPropertyStoredThroughField):
    """
    Primarily for legacy support and testing, adds adaptation to an interface
    when setting a field. This is most useful when the values are simple literals
    like strings.
    """

    def __init__(self, field, name=None):
        self.schema = _find_schema_from_field(field)
        super(AdaptingFieldPropertyStoredThroughField, self).__init__(field, name=name)

AdaptingFieldPropertyStoredThroughField.__set__ = _make_adapter_set(
    AdaptingFieldPropertyStoredThroughField)

def createDirectFieldProperties(__schema, omit=(), adapting=False):
    """
    Like :func:`zope.schema.fieldproperty.createFieldProperties`, except
    only creates properties for fields directly contained within the
    given schema; inherited fields from parent interfaces are assummed
    to be implemented in a base class of the current class::

      >>> from zope import interface
      >>> from nti.schema.field import TextLine, Object
      >>> class IA(interface.Interface):
      ...    a = TextLine(title=u"a")

      >>> class IB(IA):
      ...    b = Object(interface.Interface)

      >>> class A(object):
      ...    createFieldProperties(IA)

      >>> class B(object):
      ...    createDirectFieldProperties(IB, adapting=True)

      >>> 'a' in A.__dict__
      True
      >>> 'a' in B.__dict__
      False
      >>> 'b' in B.__dict__
      True


    :keyword adapting: If set to ``True`` (not the default), fields
        that implement :class:`.IObject` will use an :class:`AdaptingFieldProperty`.
    """

    __my_names = set(__schema.names())
    __all_names = set(__schema.names(all=True))

    __not_my_names = __all_names - __my_names
    __not_my_names.update(omit)

    # The existing implementation relies on getframe(1) to find the caller,
    # which is us. So we do the same and copy to the real caller
    __frame = None
    __before = None
    __before = list(locals().keys())
    createFieldProperties(__schema, omit=__not_my_names)

    __frame = sys._getframe(1) # pylint:disable=protected-access
    for k, v in list(locals().items()):
        if k not in __before:
            if adapting and sch_interfaces.IObject.providedBy(__schema[k]):
                v = AdaptingFieldProperty(__schema[k])
            __frame.f_locals[k] = v


def field_name(field):
    """
    Produce a clean version of a field's name.

    The
    :class:`zope.schema.fieldproperty.FieldPropertyStoredThroughField`
    class mangles the field name, making it difficult to trace fields
    back to their intended attribute name. This undoes that mangling
    if possible.

    The field in an interface has a normal name::

        >>> from zope.schema.fieldproperty import FieldPropertyStoredThroughField
        >>> from zope.schema import Field
        >>> from zope import interface
        >>> class IA(interface.Interface):
        ...    a = Field()
        >>> IA['a'].__name__
        'a'

    The field as stored by a ``FieldProperty`` has a normal name::

        >>> from zope.schema.fieldproperty import FieldProperty
        >>> class A(object):
        ...    createFieldProperties(IA)
        >>> A.a.__name__
        'a'

    But using a ``FieldPropertyStoredThroughField`` mangles the name
    (whether accessed through the ``FieldPropertyStoredThroughField``
    or directly)::

        >>> from zope.schema.fieldproperty import FieldPropertyStoredThroughField
        >>> class A2(object):
        ...    a = FieldPropertyStoredThroughField(IA['a'])
        >>> A2.a.__name__
        '__st_a_st'
        >>> A2.a.field.__name__
        '__st_a_st'

    This function demangles the name (whether accessed through the
    ``FieldPropertyStoredThroughField`` or directly)::

        >>> from nti.schema.fieldproperty import field_name
        >>> field_name(A2.a)
        'a'
        >>> field_name(A2.a.field)
        'a'

    Without damaging the names of regular fields or regular
    ``FieldProperty`` fields::

        >>> field_name(IA['a'])
        'a'
        >>> field_name(A.a)
        'a'

    .. versionadded:: 1.10.0
    """
    if field.__name__ and field.__name__.startswith('__st_') and field.__name__.endswith('_st'):
        return field.__name__[5:-3]
    return field.__name__
