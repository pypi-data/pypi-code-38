#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helpers for writing code that implements schemas.

This module contains code based on code originally from dm.zope.schema.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from zope import interface
from zope.deferredimport import deprecatedFrom
from zope.interface import Interface
from zope.interface import providedBy
from zope.schema import getFieldsInOrder

from .interfaces import ISchemaConfigured

__docformat__ = "restructuredtext en"

def _interface_from_spec(spec):
    """
    build an interface from interface spec *spec*.

    This should probably go into its own package (maybe ``dm.zope.interface``).

    Note: the interfaces constructed in this way may not be picklable
    (not tested). If they are indeed not picklable, they should not be stored.
    """
    # try to guess whether "spec" is an interface or specification
    #  The implementors have broken "issubclass", we therefore need
    #  more indirect (and in principle less reliable) methods
    # if issubclass(spec, Interface):
    # For example, the implementedBy object tests true, but can't be passed to getFieldsInOrder

    if hasattr(spec, 'names'):
        return spec # pragma: no cover
    return type(Interface)('FromSpec', tuple(spec), {})


def schemaitems(spec):
    """The schema part of interface specification *spec* as a list of id, field pairs."""
    iface = _interface_from_spec(spec)
    # may want to filter duplicates out or raise an exception on duplicates
    seen = set()
    items = []
    for (name, field) in getFieldsInOrder(iface):
        if name in seen:
            continue # pragma: no cover
        seen.add(name)
        items.append((name, field))
    return items


def schemadict(spec):
    """The schema part of interface specification *spec* as a ``dict``."""
    return dict(schemaitems(spec))


_marker = object()


@interface.implementer(ISchemaConfigured)
class SchemaConfigured(object):
    """Mixin class to provide configuration by the provided schema components."""

    def __init__(self, **kw):
        schema = schemadict(self.sc_schema_spec())
        for k, v in kw.items():
            # might want to control this check
            if k not in schema:
                raise TypeError('non schema keyword argument: %s' % k)
            setattr(self, k, v)
        # provide default values for schema fields not set
        for f, fields in schema.items():
            if getattr(self, f, _marker) is _marker:
                # The point of this is to avoid hiding exceptions (which the builtin
                # hasattr() does on Python 2)
                setattr(self, f, fields.default)

    # provide control over which interfaces define the data schema
    SC_SCHEMAS = None

    def sc_schema_spec(self):
        """the schema specification which determines the data schema.

        This is determined by `SC_SCHEMAS` and defaults to `providedBy(self)`.
        """
        spec = self.SC_SCHEMAS
        return spec or providedBy(self)

class PermissiveSchemaConfigured(SchemaConfigured):
    """
    A mixin subclass of :class:`SchemaConfigured` that allows
    for extra keywords (those not defined in the schema) to silently be ignored.
    This is an aid to evolution of code and can be helpful in testing.

    To allow for one-by-one conversions and updates, this class defines an attribute
    ``SC_PERMISSIVE``, defaulting to True, that controls this behaviour.
    """

    SC_PERMISSIVE = True

    def __init__(self, **kwargs):
        if not self.SC_PERMISSIVE:
            super(PermissiveSchemaConfigured, self).__init__(**kwargs)
        else:
            _schema = schemadict(self.sc_schema_spec())
            kwargs = {k: kwargs[k] for k in kwargs if k in _schema}
            super(PermissiveSchemaConfigured, self).__init__(**kwargs)


deprecatedFrom("Moved to nti.schema.eqhash",
               "nti.schema.eqhash",
               'EqHash',
               '_superhash')
