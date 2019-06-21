"""Test functionality of the template for benchmark specifications and the
template loader.
"""

from unittest import TestCase

from benchtmpl.workflow.benchmark.loader import BenchmarkTemplateLoader

import benchtmpl.error as err


TEMPLATE_FILE_1 = './tests/files/benchmark/template_1.yaml'
TEMPLATE_FILE_ERR_1 = './tests/files/benchmark/template_2.yaml'
TEMPLATE_FILE_ERR_2 = './tests/files/benchmark/template_3.yaml'
TEMPLATE_FILE_ERR_3 = './tests/files/template/template.yaml'


class TestBenchmarkLoader(TestCase):
    """Test benchmark template serialization and the template loader."""
    def test_load_from_file(self):
        """Test loading benchmark templates from a valid and invalid template
        files.
        """
        loader = BenchmarkTemplateLoader()
        template = loader.load(TEMPLATE_FILE_1)
        self.assertEqual(len(template.parameters), 3)
        for key in ['names', 'sleeptime', 'greeting']:
            self.assertTrue(key in template.parameters)
        self.assertTrue(len(template.schema.columns), 3)
        # Test error cases
        with self.assertRaises(err.InvalidTemplateError):
            loader.load(TEMPLATE_FILE_ERR_1)
        with self.assertRaises(err.InvalidTemplateError):
            loader.load(TEMPLATE_FILE_ERR_2)
        # A plain template file without schema information will also raise
        # an error when using the benchmark loader
        with self.assertRaises(err.InvalidTemplateError):
            loader.load(TEMPLATE_FILE_ERR_3)

    def test_template_serialization(self):
        """Test template serialization."""
        loader = BenchmarkTemplateLoader()
        template = loader.load(TEMPLATE_FILE_1)
        tmpl_ser = loader.from_dict(
            loader.to_dict(template),
            identifier=template.identifier,
            base_dir=template.base_dir
        )
        self.assertEqual(template.identifier, tmpl_ser.identifier)
        self.assertEqual(template.base_dir, tmpl_ser.base_dir)
        self.assertEqual(len(tmpl_ser.parameters), 3)
        for key in ['names', 'sleeptime', 'greeting']:
            self.assertTrue(key in tmpl_ser.parameters)
        self.assertTrue(len(tmpl_ser.schema.columns), 3)


if __name__ == '__main__':
    import unittest
    unittest.main()
