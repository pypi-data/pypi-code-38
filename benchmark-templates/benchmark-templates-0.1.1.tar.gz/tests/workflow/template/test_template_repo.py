"""Test functionality of the default template repository implementation."""

import os
import shutil

from unittest import TestCase

from benchtmpl.workflow.template.base import TemplateHandle
from benchtmpl.workflow.template.loader import DefaultTemplateLoader
from benchtmpl.workflow.template.repo import TemplateRepository
from benchtmpl.workflow.template.repo import STATIC_FILES_DIR, TEMPLATE_FILE

import benchtmpl.error as err


ERR_SPEC = './tests/files/template-error-1.yaml'
JSON_SPEC = './tests/files/template/reana-template.json'
TMP_DIR = './tests/files/.tmp'
WORKFLOW_DIR = './tests/files/template'


class DummyIDFunc():
    """Dummy id function."""
    def __init__(self):
        self.count = 0

    def __call__(self):
        self.count += 1
        return '0000'


class TestTemplateRepository(TestCase):
    """Test functionality of default template repository."""
    def setUp(self):
        """Remove temporary template repository directory. The directory will
        be created when the repository is first instantiated.
        """
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def tearDown(self):
        """Remove temporary template repository directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_add_template(self):
        """Test creating templates."""
        store = TemplateRepository(base_dir=TMP_DIR)
        template = store.add_template(src_dir=WORKFLOW_DIR)
        self.validate_template_handle(template)
        # Ensure that the template handle has been serialized correctly
        f = os.path.join(store.base_dir, template.identifier, TEMPLATE_FILE)
        doc = DefaultTemplateLoader().load(f)
        d = os.path.join(store.base_dir, template.identifier, STATIC_FILES_DIR)
        self.assertTrue(os.path.isdir(d))
        # Get template and repeat tests
        self.validate_template_handle(store.get_template(template.identifier))
        store = TemplateRepository(base_dir=TMP_DIR)
        self.validate_template_handle(store.get_template(template.identifier))
        # Add template with JSON specification file
        template = store.add_template(
            src_dir=WORKFLOW_DIR,
            template_spec_file=JSON_SPEC
        )
        self.validate_template_handle(template)
        # Unknown template error
        with self.assertRaises(err.UnknownTemplateError):
            store.get_template('unknown')
        # Errors when specifying wrong parameter combination
        with self.assertRaises(ValueError):
            store.add_template()
        with self.assertRaises(ValueError):
            store.add_template(src_dir=WORKFLOW_DIR, src_repo_url=WORKFLOW_DIR)
        # Load templates with erroneous specifications
        with self.assertRaises(err.InvalidTemplateError):
            store.add_template(src_dir=WORKFLOW_DIR, template_spec_file=ERR_SPEC)
        # Error when cloning invalid repository from GitHub
        with self.assertRaises(err.InvalidTemplateError):
            store.add_template(src_repo_url='https://github.com/reanahub/reana-demo-helloworld')

    def test_delete_template(self):
        """Ensure correct return values when deleting existing and non-existing
        templates.
        """
        store = TemplateRepository(base_dir=TMP_DIR)
        template = store.add_template(src_dir=WORKFLOW_DIR)
        f = os.path.join(store.base_dir, template.identifier, TEMPLATE_FILE)
        d = os.path.join(store.base_dir, template.identifier, STATIC_FILES_DIR)
        self.assertTrue(os.path.isfile(f))
        self.assertTrue(os.path.isdir(d))
        self.assertTrue(store.delete_template(template.identifier))
        self.assertFalse(os.path.isfile(f))
        self.assertFalse(os.path.isdir(d))
        self.assertFalse(store.delete_template(template.identifier))
        # Test deleting after store object is re-instantiated
        template = store.add_template(src_dir=WORKFLOW_DIR)
        store = TemplateRepository(base_dir=TMP_DIR)
        self.assertTrue(store.delete_template(template.identifier))
        self.assertFalse(store.delete_template(template.identifier))

    def test_error_for_id_func(self):
        """Error when the id function cannot return unique folder identifier."""
        dummy_func = DummyIDFunc()
        store = TemplateRepository(base_dir=os.path.join(TMP_DIR), id_func=dummy_func)
        os.makedirs(os.path.join(store.base_dir, dummy_func()))
        with self.assertRaises(RuntimeError):
            store.add_template(src_dir=WORKFLOW_DIR)
        self.assertEqual(dummy_func.count, 102)

    def validate_template_handle(self, template):
        """Basic tests to validate a given template handle."""
        self.assertIsNotNone(template.identifier)
        self.assertIsNotNone(template.base_dir)
        self.assertEqual(
            template.workflow_spec['inputs']['files'],
            ['$[[code]]', '$[[names]]']
        )
        self.assertEqual(len(template.parameters), 4)
        self.assertTrue(os.path.isfile(os.path.join(template.base_dir, 'code/helloworld.py')))
        self.assertTrue(os.path.isfile(os.path.join(template.base_dir, 'inputs/names.txt')))


if __name__ == '__main__':
    import unittest
    unittest.main()
