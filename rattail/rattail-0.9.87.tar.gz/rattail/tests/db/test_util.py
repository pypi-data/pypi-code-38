# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from unittest import TestCase

from rattail.db import util


class TestFunctions(TestCase):

    def test_normalize_full_name(self):
        name = util.normalize_full_name(None, None)
        self.assertEqual(name, "")

        name = util.normalize_full_name("Fred", None)
        self.assertEqual(name, "Fred")

        name = util.normalize_full_name(None, "Flintstone")
        self.assertEqual(name, "Flintstone")

        name = util.normalize_full_name("Fred", "Flintstone")
        self.assertEqual(name, "Fred Flintstone")

        name = util.normalize_full_name("  Fred  ", "  Flintstone  ")
        self.assertEqual(name, "Fred Flintstone")

    def test_normalize_phone_number(self):
        number = util.normalize_phone_number(None)
        self.assertIsNone(number)

        number = util.normalize_phone_number('417-555-1234')
        self.assertEqual(number, '4175551234')

        number = util.normalize_phone_number('  (417) 555-1234  ')
        self.assertEqual(number, '4175551234')

    def test_format_phone_number(self):
        number = util.format_phone_number(None)
        self.assertIsNone(number)

        number = util.format_phone_number('417-555-1234')
        self.assertEqual(number, '(417) 555-1234')

        number = util.format_phone_number('  (417) 555-1234  ')
        self.assertEqual(number, '(417) 555-1234')
