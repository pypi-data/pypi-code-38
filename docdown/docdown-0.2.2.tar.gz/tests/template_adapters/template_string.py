# -*- coding: utf-8 -*-

"""
test_template_string
----------------------------------

Tests for `docdown.template_adapters.template_string` module.
"""

from __future__ import absolute_import, unicode_literals, print_function

import unittest

from docdown.template_adapters import template_string


class TemplateStringAdapterTest(unittest.TestCase):

    def test_render(self):
        template = 'Hi, my name is $name'
        context = {'name': 'Justin'}
        adapter = template_string.TemplateStringAdapter()
        result = adapter.render(template, context)

        expected = 'Hi, my name is Justin'
        self.assertEqual(expected, result)

    def test_render_with_default_context(self):
        template = 'Hi, my name is Justin'
        adapter = template_string.TemplateStringAdapter()
        result = adapter.render(template)

        expected = 'Hi, my name is Justin'
        self.assertEqual(expected, result)
