#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interfaces describing the events and fields this package uses.

Also utility functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import traceback

from zope.deprecation import deprecated

from zope.schema import Text
from zope.schema import TextLine
from zope.interface import Interface
from zope.interface import Attribute
from zope.interface import providedBy
from zope.interface import implementer
from zope.schema import interfaces as sch_interfaces
try:
    from zope.schema._bootstrapfields import BeforeObjectAssignedEvent
except ImportError: # pragma: no cover
    # BWC for older zope.schema.
    from zope.schema._field import BeforeObjectAssignedEvent

__docformat__ = "restructuredtext en"

# pylint:disable=inherit-non-class,no-self-argument

class IBeforeSchemaFieldAssignedEvent(Interface):
    """
    An event sent when certain schema fields will be assigning an
    object to a property of another object.

    The interface
    :class:`zope.schema.interfaces.IBeforeObjectAssignedEvent` is a
    sub-interface of this one once this module is imported.
    """
    object = Attribute(u"The object that is going to be assigned. Subscribers may modify this")

    name = Attribute(u"The name of the attribute under which the object will be assigned.")

    context = Attribute(u"The context object where the object will be assigned to.")

# Make this a base of the zope interface so our handlers
# are compatible. This is dangerous if any lookups or registrations have already been done,
# as zope.interface maintains a cache of these things.
sch_interfaces.IBeforeObjectAssignedEvent.__bases__ = (IBeforeSchemaFieldAssignedEvent,)

@implementer(IBeforeSchemaFieldAssignedEvent)
class BeforeSchemaFieldAssignedEvent(object):

    def __init__(self, obj, name, context):
        self.object = obj
        self.name = name
        self.context = context

class IBeforeTextAssignedEvent(IBeforeSchemaFieldAssignedEvent):
    """
    Event for assigning text.
    """

    object = Text(title=u"The text being assigned.")

class IBeforeTextLineAssignedEvent(IBeforeTextAssignedEvent):  # ITextLine extends IText
    """
    Event for assigning text lines.
    """

    object = TextLine(title=u"The text being assigned.")

class IBeforeContainerAssignedEvent(IBeforeSchemaFieldAssignedEvent):
    """
    Event for assigning containers (__contains__).
    """

class IBeforeIterableAssignedEvent(IBeforeContainerAssignedEvent):
    """
    Event for assigning iterables.
    """

class IBeforeCollectionAssignedEvent(IBeforeIterableAssignedEvent):
    """
    Event for assigning collections.
    """

    object = Attribute(u"The collection being assigned. May or may not be mutable.")

class IBeforeSetAssignedEvent(IBeforeCollectionAssignedEvent):
    """
    Event for assigning sets.
    """

class IBeforeSequenceAssignedEvent(IBeforeCollectionAssignedEvent):
    """
    Event for assigning sequences.
    """

    object = Attribute(u"The sequence being assigned. May or may not be mutable.")

class IBeforeDictAssignedEvent(IBeforeIterableAssignedEvent):
    """
    Event for assigning dicts.
    """

# The hierarchy is IContainer > IIterable > ICollection > ISequence > [ITuple, IList]
# Also:         IContainer > IIterable > IDict
# Also:         IContainer > IIterable > ISet

@implementer(IBeforeTextAssignedEvent)
class BeforeTextAssignedEvent(BeforeSchemaFieldAssignedEvent):
    pass

@implementer(IBeforeTextLineAssignedEvent)
class BeforeTextLineAssignedEvent(BeforeTextAssignedEvent):
    pass


@implementer(IBeforeCollectionAssignedEvent)
class BeforeCollectionAssignedEvent(BeforeSchemaFieldAssignedEvent):
    object = None

@implementer(IBeforeSequenceAssignedEvent)
class BeforeSequenceAssignedEvent(BeforeCollectionAssignedEvent):
    pass

@implementer(IBeforeSetAssignedEvent)
class BeforeSetAssignedEvent(BeforeCollectionAssignedEvent):
    pass

@implementer(IBeforeDictAssignedEvent)
class BeforeDictAssignedEvent(BeforeSchemaFieldAssignedEvent):
    pass

BeforeObjectAssignedEvent = BeforeObjectAssignedEvent


# Set up the alias for InvalidValue. We need to use an alias so that
# try/except and subclass works as expected. The unfortunate side
# effect is that to preserve the constructor we need to swizzle the
# __init__ of sch_interfaces.InvalidValue (the swizzling is harmless;
# in zope.schema 4.7, InvalidValue inherits the Exception constructor,
# which forbids any kwargs but allows arbitrary *args; we keep that
# behaviour). This is deprecated and will be removed in the future.
InvalidValue = sch_interfaces.InvalidValue

def _InvalidValue__init__(self, *args, **kwargs):
    field = kwargs.pop('field', None)
    value = kwargs.pop('value', None)
    if kwargs:
        raise TypeError("Too many kwargs for function InvalidValue")
    # like normal
    sch_interfaces.ValidationError.__init__(self, *args)
    if field is not None or value is not None:
        self.with_field_and_value(field, value)


sch_interfaces.InvalidValue.__init__ = _InvalidValue__init__

del _InvalidValue__init__

deprecated('InvalidValue',
           "Use zope.schema.interfaces.InvalidValue.with_field_and_value.")

assert hasattr(sch_interfaces.InvalidValue, 'value')
assert hasattr(sch_interfaces.ValidationError, 'field')


class IFromObject(Interface):
    """
    Something that can convert one type of object to another,
    following validation rules (see :class:`zope.schema.interfaces.IFromUnicode`)
    """

    def fromObject(obj):
        """
        Attempt to convert the object to the required type following
        the rules of this object.  Raises a TypeError or
        :class:`zope.schema.interfaces.ValidationError` if this isn't
        possible.
        """

class IVariant(sch_interfaces.IField, IFromObject):
    """
    Similar to :class:`zope.schema.interfaces.IObject`, but
    representing one of several different types.

    If :meth:`fromObject` or :meth:`validate` fails, it should raise a
    :class:`VariantValidationError`.
    """

class VariantValidationError(sch_interfaces.ValidationError):
    """
    An error raised when a value is not suitable for any of the fields
    of the variant.

    The `errors` attribute is an ordered sequence of validation errors,
    with one raised by each field of the variant in turn.

    .. versionadded:: 1.8.0
    """

    #: A sequence of validation errors
    errors = ()

    def __init__(self, field, value, errors):
        super(VariantValidationError, self).__init__()
        self.with_field_and_value(field, value)
        self.errors = errors

    def _ex_details(self):
        lines = []
        for e in self.errors:
            info = traceback.format_exception_only(type(e), e)
            # Trim trailing newline
            info[-1] = info[-1].rstrip()
            lines.append('\n'.join(info))
        return lines

    def _with_details(self, opening, detail_formatter):
        lines = ['      ' + e for e in self._ex_details()]
        lines.append('    Field: ' + detail_formatter(self.field))
        lines.append('    Value: ' + detail_formatter(self.value))
        lines.append(opening)
        lines.reverse()
        return '\n'.join(lines)

    def __str__(self):
        s = super(VariantValidationError, self).__str__()
        return self._with_details(s, str)

    def __repr__(self):
        s = super(VariantValidationError, self).__repr__()
        return self._with_details(s, repr)

class IListOrTuple(sch_interfaces.IList):
    pass

def find_most_derived_interface(ext_self, iface_upper_bound, possibilities=None):
    """
    Search for the most derived version of the interface `iface_upper_bound`
    implemented by `ext_self` and return that. Always returns at least `iface_upper_bound`

    :keyword possibilities: An iterable of schemas to consider. If not given,
        all the interfaces provided by ``ext_self`` will be considered.
    """
    if possibilities is None:
        possibilities = providedBy(ext_self)
    _iface = iface_upper_bound
    for iface in possibilities:
        if iface.isOrExtends(_iface):
            _iface = iface
    return _iface

try:
    from dm.zope.schema.interfaces import ISchemaConfigured as _ISchemaConfigured
except ImportError:
    _ISchemaConfigured = Interface

class ISchemaConfigured(_ISchemaConfigured):
    """
    marker interface for ``SchemaConfigured`` classes.

    Used to facilitate the registration of forms and views.
    """
