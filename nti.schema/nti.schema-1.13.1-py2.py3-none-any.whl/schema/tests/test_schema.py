#!/usr/bin/env python

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904


from hamcrest import is_not
from hamcrest import contains

from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import calling
from hamcrest import raises
does_not = is_not

import unittest

from zope import interface
from zope.component import eventtesting

from . import SchemaLayer
from . import IUnicode

from ..field import Number
from ..field import Object
from ..field import DictFromObject
from ..field import ValidTextLine as TextLine

from ..schema import PermissiveSchemaConfigured
from ..schema import SchemaConfigured


from ..interfaces import IBeforeDictAssignedEvent


class TestMisc(unittest.TestCase):

    def test_fixup_name(self):
        from zope.schema.fieldproperty import FieldPropertyStoredThroughField

        field = Object(IUnicode)
        field.__name__ = 'field'

        field_property = FieldPropertyStoredThroughField(field)
        field = field_property.field

        assert_that(field, has_property('__name__', '__st_field_st'))
        assert_that(field, has_property('__fixup_name__', 'field'))

class TestSchemaConfigured(unittest.TestCase):

    def test_init(self):
        class IA(interface.Interface):
            field = Number()

        @interface.implementer(IA)
        class A(PermissiveSchemaConfigured):
            pass

        # All of these are valid ways to call it
        A()
        A(thing='abc')
        a = A(field=1)
        assert_that(a, has_property('field', 1))

        # But we can flip off the extra
        A.SC_PERMISSIVE = False
        A()
        assert_that(calling(A).with_args(thing=1),
                    raises(TypeError, 'non schema keyword'))
        a = A(field=1)
        assert_that(a, has_property('field', 1))

    def test_readonly(self):
        from nti.schema.fieldproperty import createDirectFieldProperties
        class IA(interface.Interface):
            field = Number(readonly=True,
                           required=False,
                           default=1)

        @interface.implementer(IA)
        class A(SchemaConfigured):
            createDirectFieldProperties(IA)

        a = A()
        assert_that(a, has_property('field', 1))

    def test_property_raises_exception(self):
        # https://github.com/NextThought/nti.schema/issues/11
        class IA(interface.Interface):
            field = Number(readonly=True,
                           required=False,
                           default=1)

        @interface.implementer(IA)
        class A(SchemaConfigured):
            @property
            def field(self):
                raise ValueError("bad field")

        # We can still create it without raising an AttributeError;
        # in fact, the ValueError is propagated
        assert_that(calling(A), raises(ValueError, "bad field"))


class TestConfigured(unittest.TestCase):

    layer = SchemaLayer


    def test_dict(self):

        dict_field = DictFromObject(key_type=TextLine(), value_type=Number())
        dict_field.__name__ = 'dict'

        class X(object):
            pass

        x = X()
        dict_field.set(x, dict_field.fromObject({u'k': u'1'}))

        assert_that(x, has_property('dict', {u'k': 1.0}))

        events = eventtesting.getEvents(IBeforeDictAssignedEvent)
        assert_that(events, has_length(1))
        assert_that(events, contains(has_property('object', {'k': 1.0})))
