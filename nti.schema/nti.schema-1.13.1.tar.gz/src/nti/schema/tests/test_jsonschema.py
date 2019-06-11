#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for jsonschema.py
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports
import unittest

from zope.interface import Interface
from zope.interface import Attribute

from .. import jsonschema
from ..field import DecodingValidTextLine
from ..field import ListOrTuple
from ..field import Dict
from ..field import List
from ..field import Real
from ..field import Rational
from ..field import Complex
from ..field import Integral

# ABCs
from ..field import Sequence
from ..field import IndexedIterable
from ..field import MutableSequence

from ..field import Mapping
from ..field import MutableMapping


from hamcrest import assert_that
from hamcrest import has_entry
from hamcrest import is_
from hamcrest import has_length
from hamcrest import has_key
from hamcrest import is_not
from hamcrest import same_instance
from hamcrest import none
does_not = is_not


__docformat__ = "restructuredtext en"


#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904,inherit-non-class,no-method-argument

class TranslateTestSchema(jsonschema.JsonSchemafier):

    def _translate(self, text):
        return text + self.context


class TestJsonSchemafier(unittest.TestCase):

    def test_application_info(self):

        app_info = {
            'text_key': u'a value',
            'byte_key': b'bytes',
            'int_key': 7,
            'list_key': [42,]
        }

        class IA(Interface):

            field = Attribute("A field")
            field.setTaggedValue(jsonschema.TAG_APPLICATION_INFO, app_info)

        schema = TranslateTestSchema(IA, context=u' TEST').make_schema()

        assert_that(schema, has_key("field"))
        field = schema['field']
        assert_that(field, has_key("application_info"))
        # The dict itself was copied
        assert_that(field['application_info'], is_not(same_instance(app_info)))
        # as were its contents
        assert_that(field['application_info'], has_entry('list_key', is_([42])))
        assert_that(field['application_info'],
                    has_entry('list_key', is_not(same_instance(app_info['list_key']))))

        # Text strings were translated
        assert_that(field['application_info'], has_entry('text_key', u'a value TEST'))

        # Byte strings were not (is that even legel in json?)
        assert_that(field['application_info'], has_entry('byte_key', b'bytes'))

    def test_excludes(self):

        class IA(Interface):

            def method():
                "A method"

            _thing = Attribute("A private attribute")

            hidden = Attribute("Hidden attribute")
            hidden.setTaggedValue(jsonschema.TAG_HIDDEN_IN_UI, True)

        schema = jsonschema.JsonSchemafier(IA).make_schema()
        assert_that(schema, is_({}))

    def test_readonly_override(self):
        class IA(Interface):

            field = Attribute("A field")

        schema = jsonschema.JsonSchemafier(IA, readonly_override=True).make_schema()
        assert_that(schema, has_entry('field', has_entry('readonly', True)))

    def test_ui_type(self):
        class IA(Interface):

            field = Attribute("A field")
            field.setTaggedValue(jsonschema.TAG_UI_TYPE, 'MyType')

        schema = jsonschema.JsonSchemafier(IA).make_schema()
        assert_that(schema, has_entry('field', has_entry('type', 'MyType')))

    def test_type_from_types(self):
        from zope.schema import Object
        from nti.schema.field import Variant

        def _assert_type(t, name='field',
                         **kwargs):
            schema = TranslateTestSchema(IA, context=' TEST').make_schema()
            assert_that(schema, has_entry(name, has_entry('type', t)))
            for nested_name, matcher in kwargs.items():
                assert_that(schema, has_entry(name, has_entry(nested_name, matcher)))

            return schema

        class IUnderlyingA(Interface):

            text_field = DecodingValidTextLine(title=u'nested text',
                                               min_length=5)

            hidden_text_field = DecodingValidTextLine()

        class IUnderlyingB(Interface):

            int_field = Integral()

        class IA(Interface):

            field = Attribute("A field")

            field2 = DecodingValidTextLine(title=u'A title',
                                           description=u'A description')

            list_field = List(DecodingValidTextLine())
            list_or_tuple_field = ListOrTuple(Real())
            dict_field = Dict(DecodingValidTextLine(), Real())
            mapping_field = Mapping()
            mmapping_field = MutableMapping()
            sequence_field = Sequence()
            msequence_field = MutableSequence()
            iiterable_field = IndexedIterable()

            real_field = Real()
            rational_field = Rational()
            complex_field = Complex()
            integral_field = Integral()

            object_field = Object(IUnderlyingA, required=True)
            variant_field = Variant([Object(IUnderlyingA),
                                     Object(IUnderlyingB),
                                     DecodingValidTextLine()])

            hidden_object_field = Object(IUnderlyingA, required=True)

        IA['field']._type = str
        _assert_type('string')

        IA['field']._type = (str,)
        _assert_type('string')


        IA['field']._type = float
        _assert_type('float')

        IA['field']._type = (float,)
        _assert_type('float')

        IA['field']._type = int
        _assert_type('int')

        IA['field']._type = (int,)
        _assert_type('int')

        IA['field']._type = bool
        _assert_type('bool')

        _assert_type('string', 'field2',
                     base_type='string',
                     title=u'A title TEST',
                     description=u'A description TEST')

        _assert_type('list', 'list_field', value_type=has_entry('type', 'string'))
        _assert_type('list', 'list_or_tuple_field')
        _assert_type('list', 'sequence_field')
        _assert_type('list', 'msequence_field',
                     unique=False, value_type=none(), min_length=0, max_length=none())
        _assert_type('list', 'iiterable_field')

        _assert_type('dict', 'dict_field',
                     key_type=has_entry('type', 'string'),
                     value_type=has_entry('type', 'Real'))
        _assert_type('dict', 'mapping_field')
        _assert_type('dict', 'mmapping_field')

        _assert_type('Real', 'real_field', base_type='float')
        _assert_type('Rational', 'rational_field',
                     base_type='float', max=none(), min=none())
        _assert_type('Complex', 'complex_field', base_type='float')
        _assert_type('Integral', 'integral_field', base_type='int')

        _assert_type('Object', 'object_field',
                     schema=has_entry('text_field', has_entry('min_length', 5)))

        # Now hiding some fields
        # Top-level fields can be hidden
        IA['hidden_object_field'].setTaggedValue(jsonschema.TAG_HIDDEN_IN_UI, True)

        # Fields of a schema nested in an object can be hidden.
        IUnderlyingA['hidden_text_field'].setTaggedValue(jsonschema.TAG_HIDDEN_IN_UI, True)

        # A field of a variant can be hidden
        IA['variant_field'].fields[2].setTaggedValue(jsonschema.TAG_HIDDEN_IN_UI, True)
        # All fields of lists and dicts can be hidden.
        IA['dict_field'].key_type.setTaggedValue(jsonschema.TAG_HIDDEN_IN_UI, True)
        IA['dict_field'].value_type.setTaggedValue(jsonschema.TAG_HIDDEN_IN_UI, True)
        IA['list_field'].value_type.setTaggedValue(jsonschema.TAG_HIDDEN_IN_UI, True)


        schema = _assert_type('Variant', 'variant_field',
                              value_type_options=has_length(2))
        variant_schema_values = schema['variant_field']['value_type_options']
        assert_that(variant_schema_values[0], has_entry('type', 'Object'))

        assert_that(schema, does_not(has_key('hidden_object_field')))
        assert_that(schema['object_field']['schema'], does_not(has_key('hidden_text_field')))

        assert_that(schema['list_field'], has_entry('value_type', None))
        assert_that(schema['dict_field'], has_entry('value_type', None))
        assert_that(schema['dict_field'], has_entry('key_type', None))
