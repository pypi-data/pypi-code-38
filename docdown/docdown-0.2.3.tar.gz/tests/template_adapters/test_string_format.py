# -*- coding: utf-8 -*-

"""
test_string_format
----------------------------------

Tests for `docdown.template_adapters.string_format` module.
"""

from __future__ import absolute_import, unicode_literals, print_function

import unittest

from docdown.template_adapters import string_format


class StringFormatAdapterTest(unittest.TestCase):

    def test_render(self):
        template = 'Hi, my name is {name}'
        context = {'name': 'Justin'}
        adapter = string_format.StringFormatAdapter()
        result = adapter.render(template, context)

        expected = 'Hi, my name is Justin'
        self.assertEqual(expected, result)

    def test_render_default_context(self):
        template = 'Hi, my name is Justin'
        adapter = string_format.StringFormatAdapter()
        result = adapter.render(template)

        expected = 'Hi, my name is Justin'
        self.assertEqual(expected, result)

    def test_render_missing_placeholders(self):
        """
        Test that rendering where a placeholder is in the string but not in the context
        renders an empty string for that string.
        """

        template = 'Hi, my name is {name}'
        context = {}
        adapter = string_format.StringFormatAdapter()
        result = adapter.render(template, context)

        expected = 'Hi, my name is '
        self.assertEqual(expected, result)
