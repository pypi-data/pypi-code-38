"""Test basic token scanner functionality to collect template parameter values
from standard input.
"""

from unittest import TestCase

from benchtmpl.io.scanner import Scanner, ListReader
from benchtmpl.workflow.parameter.base import TemplateParameter

import benchtmpl.workflow.parameter.declaration as pd


class TestScanner(TestCase):
    def test_propmpt(self):
        """Test generated prompts when reading parameter values from standard
        input.
        """
        # BOOL
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_BOOL
        ))).prompt()
        self.assertEqual(p, 'ABC (bool): ')
        # FILE
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_FILE
        ))).prompt()
        self.assertEqual(p, 'ABC (file): ')
        # FLOAT
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_DECIMAL
        ))).prompt()
        self.assertEqual(p, 'ABC (decimal): ')
        # INTEGER
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_INTEGER
        ))).prompt()
        self.assertEqual(p, 'ABC (integer): ')
        # STRING
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_STRING
        ))).prompt()
        self.assertEqual(p, 'ABC (string): ')
        # Default values in prompts
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_INTEGER,
            default_value=100
        ))).prompt()
        self.assertEqual(p, 'ABC (integer) [default 100]: ')
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_STRING,
            default_value=100
        ))).prompt()
        self.assertEqual(p, 'ABC (string) [default \'100\']: ')

    def test_scan_default_values(self):
        """Test return of default values when reading empty input."""
        sc = Scanner(reader=ListReader(5 * ['']))
        self.assertEqual(sc.next_int(default_value=11), 11)
        self.assertEqual(sc.next_float(default_value=1.23), 1.23)
        self.assertFalse(sc.next_bool(default_value=False))
        self.assertEqual(sc.next_file(default_value='file.txt'), 'file.txt')
        self.assertEqual(sc.next_string(default_value='Default text'), 'Default text')

    def test_scan_scalar_values(self):
        """Test parsing of scalar tokens."""
        sc = Scanner(reader=ListReader(['3', '34.56', 'FALSE', 'y', 'data/names.txt', 'Some text']))
        self.assertEqual(sc.next_int(), 3)
        self.assertEqual(sc.next_float(), 34.56)
        self.assertFalse(sc.next_bool())
        self.assertTrue(sc.next_bool())
        self.assertEqual(sc.next_file(), 'data/names.txt')
        self.assertEqual(sc.next_string(), 'Some text')
        # Value errors when parsing invalid tokens
        sc = Scanner(reader=ListReader(['3', 'FALSE', 'data/names.txt']))
        with self.assertRaises(ValueError):
            sc.next_bool()
        with self.assertRaises(ValueError):
            sc.next_int()
        with self.assertRaises(ValueError):
            sc.next_float()


if __name__ == '__main__':
    import unittest
    unittest.main()
