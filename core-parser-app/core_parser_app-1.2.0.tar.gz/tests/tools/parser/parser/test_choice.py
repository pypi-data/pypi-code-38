""" Tests for XSDParser - choice
"""
from os.path import join, dirname, abspath
from unittest.case import TestCase

from core_parser_app.tools.parser.parser import XSDParser
from tests.test_utils import DataHandler
from xml_utils.commons.constants import LXML_SCHEMA_NAMESPACE, SCHEMA_NAMESPACE
from xml_utils.xsd_tree.xsd_tree import XSDTree

# FIXME: use django finder
RESOURCES_PATH = join(dirname(abspath(__file__)), '..', 'data')


class ParserCreateChoiceTestSuite(TestCase):
    """
    """

    def setUp(self):
        choice_data = join(RESOURCES_PATH, 'parser', 'choice')
        self.choice_data_handler = DataHandler(choice_data)

        # Set default namespace
        self.namespace = LXML_SCHEMA_NAMESPACE
        self.namespaces = {'xs': SCHEMA_NAMESPACE}

        # Get an instance of the XSDParser
        self.parser = XSDParser()

    def test_create_element_basic(self):
        xsd_files = join('element', 'basic')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.namespaces)[0]

        result_string = self.parser.generate_choice(xsd_element, xsd_tree, full_path='/root')

        expected_element = self.choice_data_handler.get_json(xsd_files)

        self.assertDictEqual(expected_element, result_string)

    def test_create_element_unbounded(self):
        xsd_files = join('element', 'unbounded')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.namespaces)[0]

        result_string = self.parser.generate_choice(xsd_element, xsd_tree, full_path='/root')

        expected_element = self.choice_data_handler.get_json(xsd_files)

        self.assertDictEqual(expected_element, result_string)

    def test_create_sequence_basic(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.namespaces)[0]

        result_string = self.parser.generate_choice(xsd_element, xsd_tree, full_path='/root')

        expected_element = self.choice_data_handler.get_json(xsd_files)

        self.assertDictEqual(expected_element, result_string)

    def test_create_sequence_unbounded(self):
        xsd_files = join('sequence', 'unbounded')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.namespaces)[0]

        result_string = self.parser.generate_choice(xsd_element, xsd_tree, full_path='/root')

        expected_element = self.choice_data_handler.get_json(xsd_files)

        self.assertDictEqual(expected_element, result_string)


class ParserReloadChoiceTestSuite(TestCase):
    """
    """

    def setUp(self):
        choice_data = join(RESOURCES_PATH, 'parser', 'choice')
        self.choice_data_handler = DataHandler(choice_data)

        # Set default namespace
        self.namespace = LXML_SCHEMA_NAMESPACE
        self.namespaces = {'xs': SCHEMA_NAMESPACE}

        # Get an instance of the XSDParser
        self.parser = XSDParser()
        self.parser.editing = True

    def test_reload_element_basic(self):
        xsd_files = join('element', 'basic')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.namespaces)[0]

        xml_tree = self.choice_data_handler.get_xml(xsd_files)
        xml_data = XSDTree.tostring(xml_tree)
        edit_data_tree = XSDTree.transform_to_xml(xml_data)

        result_string = self.parser.generate_choice(xsd_element, xsd_tree, full_path='/root',
                                                    edit_data_tree=edit_data_tree)

        expected_element = self.choice_data_handler.get_json(xsd_files+".reload")

        self.assertDictEqual(expected_element, result_string)

    def test_reload_element_unbounded(self):
        xsd_files = join('element', 'unbounded')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.namespaces)[0]

        xml_tree = self.choice_data_handler.get_xml(xsd_files)
        xml_data = XSDTree.tostring(xml_tree)
        edit_data_tree = XSDTree.transform_to_xml(xml_data)

        result_string = self.parser.generate_choice(xsd_element, xsd_tree, full_path='/root',
                                                    edit_data_tree=edit_data_tree)

        expected_element = self.choice_data_handler.get_json(xsd_files+".reload")

        self.assertDictEqual(expected_element, result_string)

    def test_reload_sequence_basic(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.namespaces)[0]

        xml_tree = self.choice_data_handler.get_xml(xsd_files)
        xml_data = XSDTree.tostring(xml_tree)
        edit_data_tree = XSDTree.transform_to_xml(xml_data)

        result_string = self.parser.generate_choice(xsd_element, xsd_tree, full_path='/root',
                                                    edit_data_tree=edit_data_tree)

        expected_element = self.choice_data_handler.get_json(xsd_files+".reload")

        self.assertDictEqual(expected_element, result_string)

    def test_reload_sequence_unbounded(self):
        xsd_files = join('sequence', 'unbounded')
        xsd_tree = self.choice_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath('/xs:schema/xs:complexType/xs:choice',
                                     namespaces=self.namespaces)[0]

        xml_tree = self.choice_data_handler.get_xml(xsd_files)
        xml_data = XSDTree.tostring(xml_tree)
        edit_data_tree = XSDTree.transform_to_xml(xml_data)

        result_string = self.parser.generate_choice(xsd_element, xsd_tree, full_path='/root',
                                                    edit_data_tree=edit_data_tree)

        expected_element = self.choice_data_handler.get_json(xsd_files+".reload")

        self.assertDictEqual(expected_element, result_string)
