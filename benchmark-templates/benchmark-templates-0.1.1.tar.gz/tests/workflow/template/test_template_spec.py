"""Test TemplateHandle functionality."""

from unittest import TestCase

from benchtmpl.io.files.base import FileHandle
from benchtmpl.workflow.parameter.base import TemplateParameter
from benchtmpl.workflow.resource.base import ResourceDescriptor, LABEL_ID
from benchtmpl.workflow.template.base import TemplateHandle
from benchtmpl.workflow.template.loader import DefaultTemplateLoader

import benchtmpl.error as err
import benchtmpl.workflow.parameter.declaration as pd
import benchtmpl.workflow.template.base as tmpl
import benchtmpl.workflow.template.loader as loader


TEMPLATE_JSON_FILE = 'tests/files/template/template.json'
TEMPLATE_YAML_FILE = 'tests/files/template/template.yaml'
TEMPLATE_ERR = './tests/files/template-error-2.yaml'


class TestTemplateHandle(TestCase):
    def test_duplicate_id(self):
        """Ensure that exception is raised if parameter identifier are not
        unique.
        """
        with self.assertRaises(err.InvalidTemplateError):
            DefaultTemplateLoader().from_dict({
                    loader.LABEL_WORKFLOW: dict(),
                    loader.LABEL_PARAMETERS: [
                        pd.parameter_declaration('A', index=1),
                        pd.parameter_declaration('B'),
                        pd.parameter_declaration('C'),
                        pd.parameter_declaration('A', index=2),
                        pd.parameter_declaration('E', index=1)
                    ]
                },
                validate=True
            )

    def test_get_parameter_references(self):
        """Test function to get all parameter references in a workflow
        specification."""
        spec = {
            'input': [
                'A',
                '$[[X]]',
                {'B': {'C': '$[[Y]]', 'D': [123, '$[[Z]]']}}
            ],
            'E': {'E': 'XYZ', 'F': 23, 'G': '$[[W]]'},
            'F': '$[[U]]',
            'G': ['$[[V]]', 123]
        }
        refs = tmpl.get_parameter_references(spec)
        self.assertEqual(refs, set(['U', 'V', 'W', 'X', 'Y', 'Z']))
        # If given parameter set as argument the elements in that set are part
        # of the result
        para = set(['A', 'B', 'X'])
        refs = tmpl.get_parameter_references(spec, parameters=para)
        self.assertEqual(refs, set(['A', 'B', 'U', 'V', 'W', 'X', 'Y', 'Z']))
        # Error if specification contains nested lists
        with self.assertRaises(err.InvalidTemplateError):
            tmpl.get_parameter_references({
                'input': [
                    'A',
                    ['$[[X]]'],
                    {'B': {'C': '$[[Y]]', 'D': [123, '$[[Z]]']}}
                ]
            })
        # Error when loading specification that references undefined parameter
        with self.assertRaises(err.UnknownParameterError):
            template = DefaultTemplateLoader().load(TEMPLATE_ERR, validate=True)

    def test_init(self):
        """Test initialization of attribuets and error cases when creating
        template instances.
        """
        th = TemplateHandle(
            workflow_spec=dict(),
            parameters=[
                TemplateParameter(pd.parameter_declaration('A')),
                TemplateParameter(pd.parameter_declaration('B'))
            ]
        )
        self.assertIsNotNone(th.identifier)
        self.assertIsNone(th.base_dir)
        th = TemplateHandle(
            identifier='ABC',
            base_dir='XYZ',
            workflow_spec=dict(),
            parameters=[
                TemplateParameter(pd.parameter_declaration('A')),
                TemplateParameter(pd.parameter_declaration('B'))
            ]
        )
        self.assertEqual(th.identifier, 'ABC')
        self.assertEqual(th.base_dir, 'XYZ')
        with self.assertRaises(err.InvalidTemplateError):
            TemplateHandle(
                workflow_spec=dict(),
                parameters=[
                    TemplateParameter(pd.parameter_declaration('A')),
                    TemplateParameter(pd.parameter_declaration('B')),
                    TemplateParameter(pd.parameter_declaration('A'))
                ]
            )

    def test_nested_parameters(self):
        """Test proper nesting of parameters for DT_LIST and DT_RECORD."""
        # Create a new TemplateHandle with an empty workflow specification and
        # a list of six parameters (one record and one list)
        template = DefaultTemplateLoader().from_dict({
                loader.LABEL_WORKFLOW: dict(),
                loader.LABEL_PARAMETERS: [
                    pd.parameter_declaration('A'),
                    pd.parameter_declaration('B', data_type=pd.DT_RECORD),
                    pd.parameter_declaration('C', parent='B'),
                    pd.parameter_declaration('D', parent='B'),
                    pd.parameter_declaration('E', data_type=pd.DT_LIST),
                    pd.parameter_declaration('F', parent='E'),
                ]
            },
            validate=True
        )
        # Parameters 'A', 'C', 'D', and 'F' have no children
        for key in ['A', 'C', 'D', 'F']:
            self.assertFalse(template.get_parameter(key).has_children())
        # Parameter 'B' has two children 'C' and 'D'
        b = template.get_parameter('B')
        self.assertTrue(b.has_children())
        self.assertEqual(len(b.children), 2)
        self.assertTrue('C' in [p.identifier for p in b.children])
        self.assertTrue('D' in [p.identifier for p in b.children])
        # Parameter 'E' has one childr 'F'
        e = template.get_parameter('E')
        self.assertTrue(e.has_children())
        self.assertEqual(len(e.children), 1)
        self.assertTrue('F' in [p.identifier for p in e.children])

    def test_serialization(self):
        """Test serialization of workflow templates."""
        template = TemplateHandle(
            identifier='ABC',
            base_dir='XYZ',
            workflow_spec=dict(),
            parameters=[
                TemplateParameter(pd.parameter_declaration('A')),
                TemplateParameter(pd.parameter_declaration('B', data_type=pd.DT_LIST)),
                TemplateParameter(pd.parameter_declaration('C', parent='B'))
            ]
        )
        doc = DefaultTemplateLoader().to_dict(template)
        parameters = DefaultTemplateLoader().from_dict(doc).parameters
        self.assertTrue(len(parameters), 2)
        self.assertTrue('A' in parameters)
        self.assertTrue('B' in parameters)
        self.assertEqual(len(parameters['B'].children), 1)
        template = DefaultTemplateLoader().from_dict(doc)
        self.assertEqual(template.identifier, 'ABC')
        # The base directory is not materialized
        self.assertIsNone(template.base_dir)
        # Invalid resource descriptor serializations
        with self.assertRaises(err.InvalidTemplateError):
            ResourceDescriptor.from_dict(dict())
        with self.assertRaises(err.InvalidTemplateError):
            ResourceDescriptor.from_dict({LABEL_ID: 'A', 'noname': 'B'})

    def test_simple_replace(self):
        """Replace parameter references in simple template with argument values.
        """
        for filename in [TEMPLATE_YAML_FILE, TEMPLATE_JSON_FILE]:
            template = DefaultTemplateLoader().load(filename)
            arguments = {
                'code': template.get_argument(
                    identifier='code',
                    value=FileHandle('code/helloworld.py')
                ),
                'names': template.get_argument(
                    identifier='names',
                    value=FileHandle('data/list-of-names.txt')
                ),
                'sleeptime': template.get_argument(
                    identifier='sleeptime',
                    value=10
                )
            }
            spec = tmpl.replace_args(
                spec=template.workflow_spec,
                arguments=arguments,
                parameters=template.parameters
            )
            self.assertEqual(spec['inputs']['files'][0], 'helloworld.py')
            self.assertEqual(spec['inputs']['files'][1], 'data/names.txt')
            self.assertEqual(spec['inputs']['parameters']['helloworld'], 'code/helloworld.py')
            self.assertEqual(spec['inputs']['parameters']['inputfile'], 'data/names.txt')
            self.assertEqual(spec['inputs']['parameters']['sleeptime'], 10)
            self.assertEqual(spec['inputs']['parameters']['waittime'], 5)

    def test_sort(self):
        """Test the sort functionality of the template list_parameters method.
        """
        # Create a new TemplateHandle with an empty workflow specification and
        # a list of five parameters
        template = DefaultTemplateLoader().from_dict({
                loader.LABEL_WORKFLOW: dict(),
                loader.LABEL_PARAMETERS: [
                    pd.parameter_declaration('A', index=1),
                    pd.parameter_declaration('B'),
                    pd.parameter_declaration('C'),
                    pd.parameter_declaration('D', index=2),
                    pd.parameter_declaration('E', index=1)
                ]
            },
            validate=True
        )
        # Get list of sorted parameter identifier from listing
        keys = [p.identifier for p in template.list_parameters()]
        self.assertEqual(keys, ['B', 'C', 'A', 'E', 'D'])


if __name__ == '__main__':
    import unittest
    unittest.main()
