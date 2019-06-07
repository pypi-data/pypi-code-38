#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-3.0

from __future__ import division, absolute_import, print_function, unicode_literals
import unittest

import json
import marshal
import six
import sqlite3

import amethyst.core.obj
from amethyst.core import ImmutableObjectException, DuplicateAttributeException
from amethyst.core import Object, Attr

class MyTest(unittest.TestCase):
    def test_ttobject(self):
        obj = Object()
        self.assertEqual(obj.dict, {}, "Initial object is empty")
        self.assertEqual(len(obj), 0, "Empty length works")

        obj = Object({})
        self.assertEqual(obj.dict, {}, "Initial object is empty")

        self.assertEqual(json.loads(obj.toJSON()), {"__class__": "__amethyst.core.obj.Object__"}, "Empty toJSON")

        obj = Object.newFromJSON('{"__amethyst.core.obj.Object__": {}}')
        obj = Object.newFromJSON('{"__class__": "__amethyst.core.obj.Object__"}')

        self.assertIsNone(obj.get("__class__"), "fromJSON removes __class__ key")

        with self.assertRaises(ValueError, msg="class verification works"):
            obj = Object.newFromJSON('{"__amethyst.core.obj.NotObject__": {}}')

        with self.assertRaises(ValueError, msg="Invalid if __class__ is missing"):
            obj.fromJSON('{}')

        self.assertFalse(amethyst.core.obj.UNIQUE1 == amethyst.core.obj.UNIQUE2)
        self.assertTrue( amethyst.core.obj.UNIQUE1 != amethyst.core.obj.UNIQUE2)

        class ObjA(Object):
            foo = Attr(int)
            bar = Attr(isa=six.text_type).strip()

        class ObjB(Object):
            foo = Attr(int)
            bar = Attr(isa=six.text_type).strip()

        class ObjC(ObjA):
            pass

        a = ObjA(foo=23, bar="plugh")
        b = ObjB(foo=23, bar="plugh")
        self.assertFalse(a == b)
        self.assertFalse(b == a)
        self.assertTrue( b != a)
        self.assertTrue( a != b)

        a = ObjA(foo=23, bar="plugh")
        c = ObjC(foo=23, bar="plugh")
        self.assertFalse(a == c)
        self.assertFalse(c == a)
        self.assertTrue( c != a)
        self.assertTrue( a != c)

        a1 = ObjA(foo=23, bar="plugh")
        a2 = ObjA(foo=23, bar="plugh")
        self.assertTrue( a1 == a2)
        self.assertFalse(a1 != a2)

        a1 = ObjA(foo=23, bar="plugh")
        a2 = ObjA(foo=23, bar="barf")
        self.assertFalse(a1 == a2)

        a1 = ObjA(foo=23, bar="plugh")
        a2 = ObjA(bar="plugh")
        self.assertFalse(a1 == a2)

        a1 = ObjA(foo=23, bar="plugh")
        a2 = ObjA()
        self.assertFalse(a1 == a2)

        a1 = ObjA()
        a2 = ObjA(foo=23, bar="plugh")
        self.assertFalse(a1 == a2)

        a1 = ObjA()
        a2 = ObjA()
        self.assertTrue(a1 == a2)

        a1 = ObjA(foo=24)
        a2 = ObjA(foo=24)
        self.assertTrue(a1 == a2)


    def test_overrides(self):
        """
        Some of our methods are explicitly allowed to be replaced. These
        tests replace them with exceptions and verify that other method
        calls don't accidentally call the overrides.
        """
        class ObjOver1(Object):
            foo = Attr(int)
            bar = Attr(isa=six.text_type).strip()

            def croak(self, *args, **kwargs):
                raise Exception("Bummer")

            items = croak
            keys = croak
            values = croak
            get = croak
            set = croak
            setdefault = croak
            direct_set = croak
            pop = croak
            update = croak
            direct_update = croak
            attr_value_ok = croak
            load_data = croak
            deflate_data = croak
            inflate_new = croak

        myobj = ObjOver1(foo=23)

        with six.assertRaisesRegex(self, Exception, r'Bummer'):
            myobj.items()

        myobj.other = 15
        self.assertEqual(myobj.other, 15)
        self.assertEqual(myobj.bar, None)
        self.assertEqual(len(myobj), 1)
        self.assertTrue("foo" in myobj)
        self.assertEqual(myobj.foo, 23)
        self.assertEqual(myobj['foo'], 23)
        del myobj['foo']
        self.assertEqual(myobj.foo, None)
        myobj.foo = 24
        self.assertEqual(myobj.foo, 24)
        myobj['foo'] = 25
        self.assertEqual(myobj.foo, 25)
        myobj.amethyst_validate_update(dict(foo=26))
        myobj.amethyst_validate_data(dict(foo=27))
        myobj.amethyst_load_data(dict(foo=28), verifyclass=False)
        self.assertEqual(myobj.foo, 28)
        self.assertNotEqual(myobj.toJSON(), '')
        myobj.fromJSON('{"foo":"29"}', verifyclass=False)
        self.assertEqual(myobj.foo, 29)


    def test_other_attrs(self):
        """Other attributes explicitly allowed and are not stored in data hash"""
        class ObjOther(Object):
            foo = Attr(int)
            bar = Attr(isa=six.text_type).strip()

        myobj = ObjOther(foo=23)
        myobj.other = 15
        self.assertEqual(myobj.other, 15)
        self.assertEqual(myobj.deflate_data().get("other", None), None)
        self.assertFalse("other" in myobj.toJSON())

        with self.assertRaises(AttributeError, msg="Getattr raises exception for names undeclared attrs"):
            myobj.undefined
        with self.assertRaises(KeyError, msg="Getitem raises exception for names undeclared attrs"):
            myobj['undefined']
        with self.assertRaises(KeyError):
            myobj['undefined'] = 42
        with self.assertRaises(KeyError):
            print(myobj['undefined'])
        self.assertEqual(myobj.deflate_data().get("undefined", None), None)
        self.assertFalse("undefined" in myobj.toJSON())

        # However, the dict interface should be for proper attrs only
        with self.assertRaises(KeyError):
            print(myobj['other'])
        with self.assertRaises(KeyError):
            myobj['other'] = 42
        self.assertEqual(myobj.other, 15)
        self.assertEqual(myobj.deflate_data().get("other", None), None)
        self.assertFalse("other" in myobj.toJSON())


    def test_README_validation(self):
        class MyObject(Object):
            amethyst_verifyclass = False
            amethyst_register_type = False
            foo = Attr(int)
            bar = Attr(isa=six.text_type).strip()

        # constructors
        myobj = MyObject({ "foo": "23", "bar": "Hello " })
        self.assertIsInstance(myobj.foo, int)
        self.assertEqual(myobj.foo, 23)
        self.assertEqual(myobj.bar, "Hello")

        myobj = MyObject(foo="23", bar="Hello ")
        self.assertIsInstance(myobj.foo, int)
        self.assertEqual(myobj.bar, "Hello")

        # assignment
        myobj["foo"] = "24"                   # Converts to int
        self.assertIsInstance(myobj.foo, int)
        self.assertEqual(myobj.foo, 24)

        myobj.foo = "25"                      # Converts to int
        self.assertIsInstance(myobj["foo"], int)
        self.assertEqual(myobj["foo"], 25)

        with self.assertRaises(ValueError):
            myobj["foo"] = "Not an int"       # Raises exception
        with self.assertRaises(ValueError):
            myobj.foo = "Not an int"          # Raises exception

        # set and update methods
        myobj.set("foo", "26")
        self.assertIsInstance(myobj.foo, int)
        self.assertEqual(myobj.foo, 26)

        myobj.update(foo="27")
        self.assertIsInstance(myobj.foo, int)
        self.assertEqual(myobj.foo, 27)

        myobj.foo = 28
        myobj.setdefault("foo", 29)
        self.assertIsInstance(myobj.foo, int)
        self.assertEqual(myobj.foo, 28)
        del myobj["foo"]
        myobj.setdefault("foo", "30")
        self.assertIsInstance(myobj.foo, int)
        self.assertEqual(myobj.foo, 30)

        with self.assertRaises(ValueError):
            myobj.set("foo", "Not an int")          # Raises exception
        with self.assertRaises(ValueError):
            myobj.update(foo="Not an int")          # Raises exception

        myobj.foo = 24
        myobj.setdefault("foo", "Not an int")       # Not an error (foo already set)
        del myobj["foo"]
        with self.assertRaises(ValueError):
            myobj.setdefault("foo", "Not an int")   # Raises exception if foo unset

        # loading fresh from dict or json
        myobj.fromJSON('{"foo": "32", "bar": "Hello1 "}')
        self.assertEqual(myobj.foo, 32)
        self.assertEqual(myobj.bar, "Hello1")
        myobj = MyObject.newFromJSON('{"foo": "33", "bar": "Hello2 "}')
        self.assertEqual(myobj.foo, 33)
        self.assertEqual(myobj.bar, "Hello2")
        myobj.load_data({"foo": "34", "bar": "Hello3 "})
        self.assertEqual(myobj.foo, 34)
        self.assertEqual(myobj.bar, "Hello3")

        # Not Validated
        myobj.direct_set("foo", "Not an int")     # DANGER: Not an exception!
        self.assertEqual(myobj.foo, "Not an int")
        myobj.foo = 42
        self.assertEqual(myobj.foo, 42)
        myobj.direct_update(foo="Not an int")     # DANGER: Not an exception!
        self.assertEqual(myobj.foo, "Not an int")


    def test_README_serialization(self):
        class ObjSer1(Object):
            foo = Attr(int)
            bar = Attr(isa=six.text_type).strip()

        class ObjSer2(Object):
            foo = Attr(int)
            bar = Attr(ObjSer1)

        myobj = ObjSer1(foo="23")
        self.assertEqual(myobj.foo + 1, 24)

        # JSON can be produced and loaded
        myobj = ObjSer1(foo=42, bar="Hello")
        json_string = myobj.toJSON()
        myobj1 = ObjSer1.newFromJSON(json_string)
        self.assertEqual(myobj.dict, myobj1.dict)

        # Even for nested objects
        myobj1 = ObjSer1(foo=12, bar="Hello")
        myobj2 = ObjSer2(foo=13, bar=myobj1)
        json_string = myobj2.toJSON()
        myobjn = ObjSer2.newFromJSON(json_string)
        self.assertEqual(myobjn.foo, 13)
        self.assertEqual(myobjn.bar.foo, 12)
        self.assertEqual(myobjn.bar.bar, "Hello")

        # Other serialization libraries
        myobj = ObjSer1(foo=42, bar="Hello")
        deflated = marshal.dumps(myobj.deflate_data())
        myobj2 = ObjSer1.inflate_new(marshal.loads(deflated))
        self.assertEqual(myobj.dict, myobj2.dict)
        self.assertTrue(myobj.dict is not myobj2.dict)

        myobj1 = ObjSer1(foo=15, bar="Hello1")
        myobj2 = ObjSer2(foo=16, bar=myobj1)
        deflated = marshal.dumps(myobj2.deflate_data())
        myobjn = ObjSer2.inflate_new(marshal.loads(deflated))
        self.assertEqual(myobjn.foo, 16)
        self.assertEqual(myobjn.bar.foo, 15)
        self.assertEqual(myobjn.bar.bar, "Hello1")

        # Type hints
        myobj = ObjSer1(foo=23)
        self.assertEqual(
            six.text_type(myobj.toJSON(sort_keys=True)),
            '{"__class__": "__test_obj.ObjSer1__", "foo": 23}'
        )

        # required by default
        myobj = ObjSer1.newFromJSON('{"__class__": "__test_obj.ObjSer1__", "foo":23}')
        self.assertEqual(myobj.foo, 23)

        with six.assertRaisesRegex(self, ValueError, r'should be __test_obj\.ObjSer1__'):
            ObjSer1.newFromJSON('{"foo":23, "bar":"plugh"}')
        with six.assertRaisesRegex(self, ValueError, r'expected __test_obj\.ObjSer1__'):
            ObjSer1.newFromJSON('{"__class__": "__test_obj.ObjSer2__", "foo":23}')

        # local override
        myobj = ObjSer1.newFromJSON('{"foo":23, "bar":"plugh"}', verifyclass=False)
        self.assertEqual(myobj.foo, 23)
        self.assertEqual(myobj.bar, "plugh")

        class ObjSer3(Object):
            amethyst_includeclass  = False
            amethyst_verifyclass   = False
            foo = Attr(int)
            bar = Attr(isa=six.text_type).strip()

        myobj = ObjSer3.newFromJSON('{"foo":"23", "bar":"plugh"}')
        self.assertEqual(myobj.toJSON(sort_keys=True), '{"bar": "plugh", "foo": 23}')


    def test_immutability(self):
        class ObjIm(Object):
            foo = Attr(int)
            bar = Attr()
            baz = Attr(float)
            bip = Attr(float)
        obj = ObjIm()

        obj.amethyst_make_immutable()
        self.assertFalse(obj.amethyst_is_mutable(), "is not mutable")

        with self.assertRaises(ImmutableObjectException, msg="Can't set fields when immutable"):
            obj["foo"] = 23

        self.assertIs(obj.amethyst_make_mutable(), obj, "make_mutable returns self")
        self.assertTrue(obj.amethyst_is_mutable(), "is mutable")
        obj["bar"] = 23

        self.assertIs(obj.amethyst_make_immutable(), obj, "make_mutable returns self")
        self.assertFalse(obj.amethyst_is_mutable(), "is not mutable")

        self.assertEqual(obj["bar"], 23, "Can read values when immutable")


    def test_subclass(self):
        class ObjSub(Object):
            foo = Attr(int)
            bar = Attr()
            baz = Attr(float)
            bip = Attr(float)

        obj = ObjSub(foo=23)
        obj["bar"] = 12

        self.assertEqual(obj.foo, 23, "Getattr works in subclass when set by constructor")
        self.assertEqual(obj.bar, 12, "Getattr works in subclass when set by setitem")
        self.assertIsNone(obj.baz, "Getattr works on uninitialized values")

        self.assertEqual(obj.dict, {"foo": 23, "bar": 12}, "No autovivification")

        obj.amethyst_make_immutable()
        self.assertIsNone(obj.bip, "Can read non-existant keys when immutable")

        obj = Object()
        with self.assertRaises(AttributeError, msg="Subclasses don't change parent attributes"):
            obj.foo

        with self.assertRaises(DuplicateAttributeException, msg="Duplicate attribute raises exception"):
            class Obj2(ObjSub):
                foo = Attr(int)

        class Obj3(ObjSub):
            jsonhooks = { "__bob__": (lambda obj: "BOB") }
            bab = Attr(int)
            flags = Attr(isa=set)

        self.assertTrue(hasattr(Obj3, "foo"), "Attrs are inherited")

        obj = Obj3()
        obj.fromJSON('{"__class__": "__test_obj.Obj3__", "bar": {"__bob__": "chaz"}, "flags": {"__set__": ["chaz"]}, "baz": "123.45"}')
        self.assertEqual(obj.bar, "BOB", "jsonhooks extensions")
        self.assertEqual(list(obj.flags)[0], "chaz", "jsonhooks extensions inherit originals")

        obj = Object()
        obj.fromJSON('{"__class__": "__amethyst.core.obj.Object__", "bab": {"__bob__": "chaz"}, "flags": {"__set__": ["chaz"]}, "baz": "123.45"}', import_strategy="sloppy")
        self.assertEqual(obj.get("bab"), {"__bob__": "chaz"}, "jsonhooks extensions do not modify base classes")


    def test_default(self):
        class Obj4(Object):
            foo = Attr(int, default=3)
            bar = Attr(default=list)
            baz = Attr(default=[])

        a = Obj4()
        b = Obj4()

        self.assertEqual(a.foo, 3, "default int a")
        self.assertEqual(b.foo, 3, "default int b")

        self.assertIsInstance(a.bar, list, "default list constructor")
        self.assertIsInstance(a.baz, list, "default list")

        self.assertFalse(a.bar is b.bar, "default list constructor initializes different objects")
        self.assertTrue(a.baz is b.baz, "default list initializes identical object")


    def test_nested(self):
        class ObjN1(Object):
            foo = Attr(int)
            bar = Attr(isa=six.text_type).strip()

        class ObjN2(Object):
            foo = Attr(int)
            bar = Attr(ObjN1)
            baz = Attr(isa=ObjN1)

        myobj1 = ObjN1(foo=12, bar="Hello")
        myobj2 = ObjN2(foo=13, bar=myobj1, baz=myobj1)
        self.assertTrue(myobj2.bar is not myobj1)        # copies object
        self.assertTrue(myobj2.bar.dict is myobj1.dict)  # shallowly
        self.assertTrue(myobj2.baz is myobj1)            # isa does not modify


    def test_integration(self):
        """
        Tests to ensure that we play well with other common libraries.

        six:
          - ensure that we can be passed to six.iteritems()

        sqlite3:
          - ensure that sqlite3.Row objects can be used to initialize objects
        """
        class Obj5(Object):
            foo = Attr(int)
            bar = Attr()
            baz = Attr(float)
            bip = Attr()

        # six.iteritems(obj)
        try:
            import six
            obj = Obj5(foo=12, bar="hi", baz=2.3)
            got = set()
            for k, v in six.iteritems(obj):
                got.add("{}={}".format(k, v))
            self.assertEqual(got, set(["foo=12", "bar=hi", "baz=2.3"]), "works with six.iteritems")

        except ImportError:
            raise unittest.SkipTest("six not installed, skipping six integration tests")

        # Object(sqlite3.Row)
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("CREATE TABLE test (foo INTEGER, bar TEXT, baz TEXT, bip TEXT)")
        conn.execute("INSERT INTO test VALUES (74, 'plugh', '12.5', NULL)")

        obj = Obj5(conn.execute('SELECT * FROM test').fetchone())
        self.assertEqual(obj.foo, 74)
        self.assertEqual(obj.bar, "plugh")
        self.assertEqual(obj.baz, 12.5)
        self.assertEqual(obj.bip, None)


if __name__ == '__main__':
    unittest.main()
