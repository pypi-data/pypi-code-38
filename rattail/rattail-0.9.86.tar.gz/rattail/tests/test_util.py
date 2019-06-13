# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

import os
import shutil
from unittest import TestCase

from rattail import util


class ImportTests(TestCase):

    def setUp(self):
        dirname = os.path.abspath(os.path.dirname(__file__))
        os.mkdir(os.path.join(dirname, 'foo'))
        with open(os.path.join(dirname, 'foo', '__init__.py'), 'w') as f:
            f.write('\n')
        with open(os.path.join(dirname, 'foo', 'bar.py'), 'w') as f:
            f.write('\n')
        os.mkdir(os.path.join(dirname, 'foo', 'baz'))
        with open(os.path.join(dirname, 'foo', 'baz', '__init__.py'), 'w') as f:
            f.write('\n')

    def tearDown(self):
        shutil.rmtree(os.path.join(os.path.dirname(__file__), 'foo'))

    def test_module_already_imported(self):
        util_module = util.import_module_path('rattail.util')
        self.assertTrue(util_module is util)

    # def test_new_module(self):
    #     dirname = os.path.abspath(os.path.dirname(__file__))

    #     foo = util.import_module_path('tests.foo')
    #     self.assertEqual(foo.__file__, os.path.abspath(
    #             os.path.join(dirname, 'foo', '__init__.py')))

    #     bar = util.import_module_path('tests.foo.bar')
    #     self.assertEqual(bar.__file__, os.path.abspath(
    #             os.path.join(dirname, 'foo', 'bar.py')))

    #     baz = util.import_module_path('tests.foo.baz')
    #     self.assertEqual(baz.__file__, os.path.abspath(
    #             os.path.join(dirname, 'foo', 'baz', '__init__.py')))

#     def test_load_object(self):
#         with open(os.path.join(os.path.dirname(__file__), 'foo', 'baz', '__init__.py'), 'w') as f:
#             f.write("""

# somevar = 42

# def somefunc():
#     return somevar * 10

# """)

#         somevar = util.load_object('tests.foo.baz:somevar')
#         self.assertEqual(somevar, 42)

#         somefunc = util.load_object('tests.foo.baz:somefunc')
#         self.assertEqual(somefunc(), 420)
