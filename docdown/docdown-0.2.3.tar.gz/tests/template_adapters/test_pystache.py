# -*- coding: utf-8 -*-

"""
test_pystache
----------------------------------

Tests for `docdown.template_adapters.pystache` module.
"""

from __future__ import absolute_import, unicode_literals, print_function

import unittest

from docdown.template_adapters import pystache


class PystacheAdapterTest(unittest.TestCase):

    def test_render(self):
        template = 'Hi, my name is {{ name }}'
        context = {'name': 'Justin'}
        adapter = pystache.PystacheAdapter()
        result = adapter.render(template, context)

        expected = 'Hi, my name is Justin'
        self.assertEqual(expected, result)

    def test_render_with_default_context(self):
        template = 'Hi, my name is Justin'
        adapter = pystache.PystacheAdapter()
        result = adapter.render(template)

        expected = 'Hi, my name is Justin'
        self.assertEqual(expected, result)
