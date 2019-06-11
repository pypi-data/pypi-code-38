#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for interfaces.py

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports
import unittest

from zope.deprecation import Suppressor

with Suppressor():
    from ..interfaces import InvalidValue

from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import none
from hamcrest import is_
from hamcrest import instance_of

__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

class TestInvalidValue(unittest.TestCase):

    def test_construct(self):
        v = InvalidValue()
        assert_that(v, has_property('value', none()))
        assert_that(v, has_property('field', none()))

        v = InvalidValue(value=1, field=1)
        assert_that(v, has_property('value', 1))
        assert_that(v, has_property('field', 1))

        with self.assertRaises(TypeError):
            InvalidValue(value=1, field=2, other=3)

    def test_subclass(self):
        kind = type('subclass', (InvalidValue,), {})
        self.test_instance(kind)
        self.test_raise_except(kind)

    def test_instance(self, kind=InvalidValue):
        from zope.schema import interfaces as sch_interfaces
        v = kind()
        self.assertIsInstance(v, sch_interfaces.InvalidValue)
        self.assertIsInstance(v, InvalidValue)

    def test_raise_except(self, kind=InvalidValue):
        # It can be caught by its own name
        with self.assertRaises(kind):
            raise kind()
        # It can be caught by the zope.schema name
        from zope.schema import interfaces as sch_interfaces
        with self.assertRaises(sch_interfaces.InvalidValue):
            raise InvalidValue()

    def test_repr(self):
        assert_that(repr(InvalidValue('foo')),
                    is_("InvalidValue('foo')"))

    def test_alias(self):
        from zope.schema import interfaces as sch_interfaces
        self.assertIs(InvalidValue, sch_interfaces.InvalidValue)
