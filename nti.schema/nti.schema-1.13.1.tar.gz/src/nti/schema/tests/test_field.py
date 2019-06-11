#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for field.py
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports
import unittest
import warnings

from zope.component import eventtesting

from zope.interface.common import interfaces as cmn_interfaces
from zope.schema import Dict

from zope.schema.fieldproperty import FieldProperty

from zope.schema.interfaces import ValidationError
from zope.schema.interfaces import InvalidURI
from zope.schema.interfaces import SchemaNotProvided
from zope.schema.interfaces import TooLong
from zope.schema.interfaces import TooShort
from zope.schema.interfaces import WrongType


from nti.schema.field import HTTPURL
from nti.schema.field import DecodingValidTextLine
from nti.schema.field import FieldValidationMixin
from nti.schema.field import Float
from nti.schema.field import IndexedIterable
from nti.schema.field import Int
from nti.schema.field import ListOrTuple
from nti.schema.field import ListOrTupleFromObject
from nti.schema.field import Number
from nti.schema.field import Object
from nti.schema.field import ObjectLen
from nti.schema.field import StrippedValidTextLine
from nti.schema.field import TupleFromObject
from nti.schema.field import UniqueIterable
from nti.schema.field import ValidDatetime
from nti.schema.field import ValidRegularExpression
from nti.schema.field import Variant
from nti.schema.field import ValidTextLine as TextLine
from nti.schema.interfaces import IBeforeDictAssignedEvent
from nti.schema.interfaces import IBeforeSequenceAssignedEvent
from nti.schema.interfaces import InvalidValue
from nti.schema.interfaces import IVariant
from nti.schema.interfaces import IFromObject
from nti.schema.interfaces import VariantValidationError
# Import from the BWC location

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from nti.schema.testing import validated_by # pylint:disable=no-name-in-module
    from nti.schema.testing import verifiably_provides # pylint:disable=no-name-in-module
    from nti.schema.testing import not_validated_by # pylint:disable=no-name-in-module


from . import IUnicode
from . import SchemaLayer

from hamcrest import assert_that
from hamcrest import calling
from hamcrest import contains
from hamcrest import contains_string
from hamcrest import equal_to
from hamcrest import has_length
from hamcrest import has_property
from hamcrest import is_
from hamcrest import is_not
from hamcrest import none
from hamcrest import raises

does_not = is_not

__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904,blacklisted-name


class TestObjectLen(unittest.TestCase):


    def test_objectlen(self):
        # If we have the inheritance messed up, we will have problems
        # creating, or we will have problems validating one part or the other.

        olen = ObjectLen(IUnicode, max_length=5)  # default val for min_length

        olen.validate(u'a')
        olen.validate(u'')

        assert_that(calling(olen.validate).with_args(object()),
                    raises(SchemaNotProvided))

        assert_that(calling(olen.validate).with_args(u'abcdef'),
                    raises(TooLong))

    def test_objectlen_short(self):
        olen = ObjectLen(IUnicode, min_length=5)

        assert_that(calling(olen.validate).with_args(u'abc'),
                    raises(TooShort))

class TestHTTPUrl(unittest.TestCase):

    def test_http_url(self):

        http = HTTPURL(__name__='foo')

        assert_that(http.fromUnicode('www.google.com'),
                    is_('http://www.google.com'))

        assert_that(http.fromUnicode('https://www.yahoo.com'),
                    is_('https://www.yahoo.com'))

        with self.assertRaises(InvalidURI) as exc:
            http.fromUnicode('mailto:jason@nextthought.com')

        exception = exc.exception
        assert_that(exception, has_property('field', http))
        assert_that(exception, has_property('value', 'mailto:jason@nextthought.com'))
        assert_that(exception, has_property('message', 'The specified URL is not valid.'))

class TestVariant(unittest.TestCase):

    def test_variant(self):

        syntax_or_lookup = Variant((Object(cmn_interfaces.ISyntaxError),
                                    Object(cmn_interfaces.ILookupError),
                                    Object(IUnicode)))

        assert_that(syntax_or_lookup, verifiably_provides(IVariant))

        # validates
        assert_that(SyntaxError(), validated_by(syntax_or_lookup))
        assert_that(LookupError(), validated_by(syntax_or_lookup))

        # doesn't validate
        assert_that(b'foo', not_validated_by(syntax_or_lookup))

        assert_that(syntax_or_lookup.fromObject(u'foo'), is_(u'foo'))

        with self.assertRaises(VariantValidationError) as exc:
            syntax_or_lookup.fromObject(object())

        assert_that(exc.exception,
                    has_property('errors',
                                 has_length(len(syntax_or_lookup.fields))))

    def test_getDoc(self):
        syntax_or_lookup = Variant((Object(cmn_interfaces.ISyntaxError),
                                    Object(cmn_interfaces.ILookupError),
                                    Object(IUnicode)))

        doc = syntax_or_lookup.getDoc()
        assert_that(doc, contains_string('.. rubric:: Possible Values'))
        assert_that(doc, contains_string('.. rubric:: Option'))

    def test_complex_variant(self):

        dict_field = Dict(key_type=TextLine(), value_type=TextLine())
        string_field = Object(IUnicode)
        list_of_numbers_field = ListOrTuple(value_type=Number())

        variant = Variant((dict_field, string_field, list_of_numbers_field))
        variant.getDoc()  # cover
        # It takes all these things
        for d in {u'k': u'v'}, u'foo', [1, 2, 3]:
            assert_that(d, validated_by(variant))

        # It rejects these by raising a VariantValidationError
        # with the same number of errors as fields
        for d in {u'k': 1}, b'foo', [1, 2, u'b']:
            assert_that(d, not_validated_by(variant))
            with self.assertRaises(VariantValidationError) as exc:
                variant.fromObject(d)

            assert_that(exc.exception, has_property("errors",
                                                    has_length(len(variant.fields))))

            with self.assertRaises(VariantValidationError) as exc:
                variant.validate(d)

            assert_that(exc.exception, has_property("errors",
                                                    has_length(len(variant.fields))))

        # A name set now is reflected down the line
        variant.__name__ = 'baz'
        for f in variant.fields:
            assert_that(f, has_property('__name__', 'baz'))

        # and in clones
        clone = variant.bind(object())
        for f in clone.fields:
            assert_that(f, has_property('__name__', 'baz'))

        # which doesn't change the original
        clone.__name__ = 'biz'
        for f in clone.fields:
            assert_that(f, has_property('__name__', 'biz'))

        for f in variant.fields:
            assert_that(f, has_property('__name__', 'baz'))

        # new objects work too
        new = Variant(variant.fields, __name__='boo')
        for f in new.fields:
            assert_that(f, has_property('__name__', 'boo'))

    def test_variant_from_object(self):
        field = Variant((TupleFromObject(HTTPURL()),))

        res = field.fromObject(['http://example.com'])
        assert_that(res, is_(('http://example.com',)))

    def test_variant_auto_convert_sequence(self):
        from zope.schema import List
        from zope.schema import Field

        string_field = Object(IUnicode)
        list_field = List(string_field)
        assert_that(list_field, does_not(verifiably_provides(IFromObject)))

        # But once we add it to a variant, it does

        variant = Variant((list_field,))

        assert_that(list_field, verifiably_provides(IFromObject))

        bound_variant = variant.bind(self)

        assert_that(bound_variant.fields[0], verifiably_provides(IFromObject))

        l = bound_variant.fromObject([u'abc'])
        assert_that(l, is_([u'abc']))

        # Doing the same with a list of a field we don't know about
        # does nothing.
        field = Field()
        list_field = List(field)
        assert_that(list_field, does_not(verifiably_provides(IFromObject)))
        variant = Variant((list_field,))
        assert_that(list_field, does_not(verifiably_provides(IFromObject)))

    def test_variant_auto_convert_mapping(self):
        from zope.schema import Dict as ZDict # pylint:disable=reimported
        from zope.schema import Field

        string_field = Object(IUnicode)
        map_field = ZDict(string_field, string_field)
        assert_that(map_field, does_not(verifiably_provides(IFromObject)))

        # But once we add it to a variant, it does

        variant = Variant((map_field,))

        assert_that(map_field, verifiably_provides(IFromObject))

        bound_variant = variant.bind(self)

        assert_that(bound_variant.fields[0], verifiably_provides(IFromObject))

        l = bound_variant.fromObject({u'abc': u'def'})
        assert_that(l, is_({u'abc': u'def'}))

        # Doing the same with a list of a field we don't know about
        # does nothing.
        map_field = ZDict(Field(), Field())
        assert_that(map_field, does_not(verifiably_provides(IFromObject)))
        variant = Variant((map_field,))
        assert_that(map_field, does_not(verifiably_provides(IFromObject)))

    def test_converts_but_not_valid(self):
        # If the schema accepts the input, but the validation refuses,
        # keep going.
        class WeirdField(Object):
            schema = IUnicode

            def validate(self, value):
                raise SchemaNotProvided().with_field_and_value(self, value)
        weird_field = WeirdField(IUnicode)
        accept_field = Number()

        field = Variant((weird_field, accept_field),
                        variant_raise_when_schema_provided=True)
        assert_that(field.fromObject("1.0"),
                    is_(1.0))

        assert_that(calling(field.validate).with_args(u'1.0'),
                    raises(SchemaNotProvided))

    def test_invalid_construct(self):
        assert_that(calling(Variant).with_args(()),
                    raises(SchemaNotProvided))

    def test_AttributeError_transformed(self):
        # Something that blows up badly on None input
        # to fromUnicode never gets there.
        from zope.schema.interfaces import RequiredMissing
        http_field = HTTPURL()
        with self.assertRaises(AttributeError):
            http_field.fromUnicode(None)

        # Gets wrapped up into a validation error by a Variant
        # (anything that does a conversion, actually).
        # We have to use a non-default (and thus non None)
        # missing value to take this code path.
        field = Variant((http_field,),
                        missing_value=self)

        with self.assertRaises(VariantValidationError) as exc:
            field.fromObject(None)

        ex = exc.exception
        assert_that(ex.errors, has_length(1))
        assert_that(ex.errors[0], is_(RequiredMissing))

        for val in repr(ex), str(ex):
            assert_that(val, contains_string("RequiredMissing"))
            assert_that(val, contains_string("Value:"))
            assert_that(val, contains_string("Field:"))

    def test_numbers_pass_unchanged(self):
        from zope.schema import Number as ZNumber

        number = ZNumber()
        variant = Variant([number])

        assert_that(variant.fromObject(10), is_(10))

    def test_None_not_passed_to_fromUnicode(self):
        # But something that can accept None
        # does get it still
        from zope.schema import Field
        class MyField(Field):

            last_value = None

            def fromUnicode(self, value):
                raise AssertionError("Should not be called")

            def validate(self, value):
                self.last_value = 42

        field = MyField()
        variant = Variant([field], required=False)
        x = variant.fromObject(None)
        assert_that(x, is_(none()))
        assert_that(field.last_value, is_(42))

    def test_missing_value_not_required(self):
        from zope.schema.interfaces import RequiredMissing
        text = TextLine()

        variant = Variant((text,), required=False)
        # None is the default missing value, and it's allowed
        assert_that(variant.fromObject(None),
                    is_(none()))

        # If we are required, though, we cannot use the missing value
        variant = Variant((text,), required=True)
        with self.assertRaises(RequiredMissing):
            variant.fromObject(None)

        # We can use arbitrary other missing values
        variant = Variant((text,), required=False, missing_value=self)
        assert_that(variant.fromObject(self),
                    is_(self))

        # And None now raises.
        with self.assertRaises(VariantValidationError):
            variant.fromObject(None)

class TestConfiguredVariant(unittest.TestCase):

    layer = SchemaLayer

    def test_nested_variants(self):
        # Use case: Chat messages are either a Dict, or a N
        # ote-like body, which itself is a list of variants

        dict_field = Dict(key_type=TextLine(), value_type=TextLine())

        string_field = Object(IUnicode)
        number_field = Number()
        list_of_strings_or_numbers = ListOrTuple(value_type=Variant((string_field, number_field)))

        assert_that([1, u'2'], validated_by(list_of_strings_or_numbers))
        assert_that({u'k': u'v'}, validated_by(dict_field))

        dict_or_list = Variant((dict_field, list_of_strings_or_numbers))

        assert_that([1, u'2'], validated_by(dict_or_list))
        assert_that({u'k': u'v'}, validated_by(dict_or_list))

        class X(object):
            pass

        x = X()
        dict_or_list.set(x, [1, u'2'])

        events = eventtesting.getEvents(IBeforeSequenceAssignedEvent)
        assert_that(events, has_length(1))
        assert_that(events, contains(has_property('object', [1, '2'])))

        eventtesting.clearEvents()

        dict_or_list.set(x, {u'k': u'v'})
        events = eventtesting.getEvents(IBeforeDictAssignedEvent)
        assert_that(events, has_length(1))
        assert_that(events, contains(has_property('object', {'k': 'v'})))

class TestValidSet(unittest.TestCase):

    def _getTargetClass(self):
        from nti.schema.field import ValidSet
        return ValidSet

    def _makeOne(self):
        return self._getTargetClass()()

    default_min_length = 0

    def test_min_length(self):
        field = self._getTargetClass()(__name__='foo')
        assert_that(field, has_property('min_length',
                                        self.default_min_length))

        class Thing(object):
            foo = None
        thing = Thing()
        field.set(thing, ())

        assert_that(thing, has_property('foo', ()))

    def test_value_type(self):
        field = self._getTargetClass()(value_type=HTTPURL())

        o = field.fromObject({'https://example.com'})
        assert_that(o, is_({'https://example.com'}))

    def test_interfaces(self):
        assert_that(self._makeOne(),
                    verifiably_provides(IFromObject))


class TestUniqueIterable(TestValidSet):

    def _getTargetClass(self):
        return UniqueIterable

    default_min_length = none()

class SequenceFromObjectMixinMixin(object):

    def _getTargetClass(self):
        raise NotImplementedError

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_accepts_missing_value(self):
        from zope.schema.interfaces import RequiredMissing
        field = self._makeOne(required=False, missing_value=None)
        assert_that(field.fromObject(None), is_(none()))

        # but if we're required, we get a different exception
        field = self._makeOne(required=True, missing_value=None)
        with self.assertRaises(RequiredMissing):
            field.fromObject(None)

        # We can change the type
        field = self._makeOne(required=False, missing_value=self)
        assert_that(field.fromObject(self), is_(self))


class TestTupleFromObject(SequenceFromObjectMixinMixin,
                          unittest.TestCase):

    def _getTargetClass(self):
        return TupleFromObject

    def test_set(self):
        field = TupleFromObject(__name__='foo')

        class Thing(object):
            foo = None

        thing = Thing()
        field.validate([1, 2])
        field.set(thing, [1, 2])
        assert_that(thing, has_property('foo', (1, 2)))

        # But arbitrary iterables not validated...
        assert_that(calling(field.validate).with_args('abc'),
                    raises(WrongType))

        # Although they can be set...
        field.set(thing, 'abc')

    def test_wrong_type_from_object(self):
        field = TupleFromObject()
        assert_that(calling(field.fromObject).with_args('abc'),
                    raises(WrongType))

    def test_valid_type_from_object_unicode(self):
        field = TupleFromObject(HTTPURL())
        res = field.fromObject(['http://example.com'])
        assert_that(res, is_(('http://example.com',)))

    def test_valid_type_from_object_object(self):
        # Nested layers of fromObject and fromUnicode
        field = TupleFromObject(Variant((HTTPURL(),)))
        res = field.fromObject(['http://example.com'])
        assert_that(res, is_(('http://example.com',)))



class TestListOrTupleFromObject(SequenceFromObjectMixinMixin,
                                unittest.TestCase):

    def _getTargetClass(self):
        return ListOrTupleFromObject

    def test_construct_with_object(self):
        field = ListOrTupleFromObject(Object(IUnicode))

        assert_that(field.value_type, verifiably_provides(IFromObject))

        # And it tries to adapt individual fields
        with self.assertRaises(TypeError) as exc:
            field.fromObject((b'abc',))

        exception = exc.exception
        self.assertEqual(exception.args[0], 'Could not adapt')

        class Conforms(object):

            def __conform__(self, iface):
                assert_that(iface, is_(IUnicode))
                return u'def'

        o = field.fromObject((Conforms(),))
        assert_that(o, is_([u'def']))

        # This works even when bound

        field = field.bind(self)
        assert_that(field.value_type, verifiably_provides(IFromObject))
        o = field.fromObject((Conforms(),))
        assert_that(o, is_([u'def']))

    def test_construct_with_bad_field(self):

        from zope.schema import Field

        with self.assertRaises(SchemaNotProvided):
            ListOrTupleFromObject(Field())


class TestIndexedIterable(unittest.TestCase):

    def test_accepts_str(self):
        field = IndexedIterable(__name__='foo')
        class Thing(object):
            foo = None

        thing = Thing()
        field.set(thing, 'abc')
        assert_that(thing, has_property('foo', 'abc'))

class TestStrippedValidTextLine(unittest.TestCase):

    def test_stripped(self):
        field = StrippedValidTextLine(__name__='foo')

        class Thing(object):
            foo = FieldProperty(field)

        assert_that(field.fromUnicode(u' abc '), equal_to(u'abc'))
        assert_that(field.fromUnicode(u' a '), equal_to(u'a'))
        assert_that(field.fromBytes(b' abc '), equal_to(u'abc'))
        assert_that(calling(setattr).with_args(Thing(), 'foo', u' abc '), raises(InvalidValue))
        assert_that(calling(setattr).with_args(Thing(), 'foo', u'abc '), raises(InvalidValue))
        assert_that(calling(setattr).with_args(Thing(), 'foo', u' abc'), raises(InvalidValue))

        # Check valid case
        Thing().foo = u'abc'
        Thing().foo = u'a'

class TestDecodingValidTextLine(unittest.TestCase):

    def test_decode(self):
        field = DecodingValidTextLine()
        res = field.validate(b'abc')
        assert_that(res, is_(u'abc'))

    def test_fromBytes(self):
        from zope.schema.interfaces import IFromBytes
        field = DecodingValidTextLine()
        assert_that(field, verifiably_provides(IFromBytes))

        val = field.fromBytes(b'abc')
        assert_that(val, is_(u'abc'))

class TestNumber(unittest.TestCase):

    def test_allow_empty(self):
        assert_that(Float().fromUnicode(''), is_(none()))
        assert_that(Int().fromUnicode(''), is_(none()))

class TestDatetime(unittest.TestCase):

    def test_validate_wrong_type(self):
        field = ValidDatetime()
        assert_that(calling(field.validate).with_args(''),
                    raises(SchemaNotProvided))

class TestFieldValidationMixin(unittest.TestCase):

    def test_one_arg(self):
        field = FieldValidationMixin()
        field.__name__ = 'foo'

        ex = SchemaNotProvided('msg').with_field_and_value(field, 'value')
        # zope.schema 4.7 automatically fills in args
        assert_that(ex.args, is_(('msg', None)))
        assert_that(ex.schema, is_('msg'))
        ex.args = ('msg',)
        try:
            field._reraise_validation_error(ex, 'value', _raise=True)
        except SchemaNotProvided:
            assert_that(ex.args, is_(('value', 'msg', 'foo')))

    def test_no_arg(self):
        field = FieldValidationMixin()
        field.__name__ = 'foo'

        ex = SchemaNotProvided().with_field_and_value(field, 'value')
        # zope.schema 4.7 automatically fills in args
        assert_that(ex.args, is_((None, None)))
        ex.args = ()
        try:
            field._reraise_validation_error(ex, 'value', _raise=True)
        except SchemaNotProvided:
            assert_that(ex.args, is_(('value', '', 'foo')))

    def test_oob(self):
        from zope.schema import Integral
        from zope.schema.interfaces import OutOfBounds
        class Field(FieldValidationMixin, Integral):
            pass

        field = Field(min=1)
        with self.assertRaises(OutOfBounds):
            field.validate(0)

    def test_random_validation_error(self):
        class Field(object):
            __name__ = ''
            def _validate(self, v):
                raise ValidationError().with_field_and_value(self, v)

        class Field2(FieldValidationMixin, Field):
            pass

        field = Field2()
        with self.assertRaises(ValidationError) as exc:
            field._validate(42)

        ex = exc.exception
        assert_that(ex.args, is_((42, '', '')))


class TestRegex(unittest.TestCase):

    def test_regex(self):
        field = ValidRegularExpression('[bankai|shikai]', flags=0)
        assert_that(field.constraint("bankai"), is_(True))
        assert_that(field.constraint("shikai"), is_(True))
        assert_that(field.constraint("Shikai"), is_(False))
        assert_that(field.constraint("foo"), is_(False))
        field = ValidRegularExpression('[bankai|shikai]')
        assert_that(field.constraint("Shikai"), is_(True))
        assert_that(field.constraint("banKAI"), is_(True))


class TestValueTypeAddingDocMixin(unittest.TestCase):

    def _getTargetClass(self):
        from nti.schema.field import _ValueTypeAddingDocMixin
        return _ValueTypeAddingDocMixin

    def test_getDoc(self):

        from zope.schema import Field

        class MyField(self._getTargetClass(), Field):
            _type = object
            accept_types = (list, tuple)

        doc = MyField().getDoc()

        assert_that(doc, contains_string(':Allowed Type: :class:`object`'))
        assert_that(doc, contains_string(':Accepted Types: :class:`list`, :class:`tuple`'))


class TestDictFromObject(SequenceFromObjectMixinMixin,
                         unittest.TestCase):

    def _getTargetClass(self):
        from nti.schema.field import DictFromObject
        return DictFromObject

    def test_interfaces(self):
        assert_that(self._makeOne(),
                    verifiably_provides(IFromObject))

    def test_accepts_mapping(self):
        from six.moves import UserDict
        from nti.schema.field import abcs

        # On Python 2, UserDict is not registered as a Mapping.
        if not issubclass(UserDict, abcs.Mapping): # pragma: no cover
            abcs.Mapping.register(UserDict)

        field = self._makeOne(key_type=Int(), value_type=Float())

        value = UserDict({'1': '42'})
        assert_that(value, is_(abcs.Mapping))
        assert_that(value, is_not(dict))

        result = field.fromObject(value)
        assert_that(result, is_(dict))
        assert_that(result, is_({1: 42.0}))

    def test_getDoc(self):
        field = self._makeOne(key_type=Int(), value_type=Float())
        doc = field.getDoc()

        assert_that(doc, contains_string('.. rubric:: Value Type'))
        assert_that(doc, contains_string('.. rubric:: Key Type'))


class Test_FieldConverter(unittest.TestCase):

    def _getTargetClass(self):
        from nti.schema.field import _FieldConverter
        return _FieldConverter

    def _makeOne(self, field=None):
        return self._getTargetClass()(field)

    def test_fromBytes(self):

        class Field(object):
            def fromBytes(self, value):
                return b'from bytes'

            def validate(self, value):
                raise WrongType

        field = Field()
        converter = self._makeOne(field)
        assert_that(converter(b''), is_(b'from bytes'))

        with self.assertRaises(WrongType) as exc:
            converter(1)

        exception = exc.exception
        assert_that(exception, has_property('field', field))
        assert_that(exception, has_property('value', 1))

    def test_validate_called_last(self):
        # If we had nothing else to do, we
        # call validate and if it doesn't raise, we return
        class Field(object):
            def validate(self, value):
                if value == 42:
                    raise ValidationError

        field = Field()
        # A bad value raises, and we fill in the field and value if
        # needed.
        converter = self._makeOne(field)
        with self.assertRaises(ValidationError) as exc:
            converter(42)

        assert_that(exc.exception.field, is_(field))
        assert_that(exc.exception.value, is_(42))

        # Otherwise we return the value we were passed
        assert_that(converter(b''), is_(b''))
        assert_that(converter(u''), is_(u''))

    def test_fromObject(self):
        # from object is only called for non-strings if
        # fromUnicode and fromBytes are implemented.
        class Field(object):
            def fromObject(self, value):
                return b'from object'

            def fromUnicode(self, value):
                return u'from unicode'

            def fromBytes(self, value):
                return b'from bytes'

        converter = self._makeOne(Field())
        assert_that(converter(b''), is_(b'from bytes'))
        assert_that(converter(u''), is_(u'from unicode'))
        assert_that(converter(1), is_(b'from object'))
