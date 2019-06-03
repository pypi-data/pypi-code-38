""" Parser unit tests for complex type
"""
from os.path import join, dirname, abspath
from unittest.case import TestCase

from core_parser_app.tools.parser.parser import XSDParser
from tests.test_utils import DataHandler
from xml_utils.commons.constants import LXML_SCHEMA_NAMESPACE, SCHEMA_NAMESPACE
from xml_utils.xsd_tree.xsd_tree import XSDTree

# FIXME: use django finder
RESOURCES_PATH = join(dirname(abspath(__file__)), "..", "data")


class ParserCreateComplexTypeTestSuite(TestCase):
    """ Element creation unit tests
    """

    def setUp(self):
        # Setup data handler
        complex_type_data = join(RESOURCES_PATH, "parser", "complex_type")
        self.complex_type_data_handler = DataHandler(complex_type_data)

        # Set default namespace
        self.namespace = LXML_SCHEMA_NAMESPACE
        self.namespaces = {"xs": SCHEMA_NAMESPACE}

        # Get an instance of the XSDParser
        self.parser = XSDParser()

    def test_create_choice_basic(self):
        xsd_files = join("choice", "basic")
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath("/xs:schema/xs:complexType", namespaces=self.namespaces)[0]

        result_string = self.parser.generate_complex_type(xsd_element, xsd_tree,
                                                          full_path="/root")

        expected_dict = self.complex_type_data_handler.get_json(xsd_files)
        self.assertDictEqual(result_string, expected_dict)

    def test_create_sequence_basic(self):
        xsd_files = join("sequence", "basic")
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath("/xs:schema/xs:complexType", namespaces=self.namespaces)[0]

        result_string = self.parser.generate_complex_type(xsd_element, xsd_tree,
                                                          full_path="/root")

        expected_dict = self.complex_type_data_handler.get_json(xsd_files)
        self.assertDictEqual(result_string, expected_dict)

    def test_create_simple_content_basic(self):
        xsd_files = join("simple_content", "basic")
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath("/xs:schema/xs:complexType", namespaces=self.namespaces)[0]

        result_string = self.parser.generate_complex_type(xsd_element, xsd_tree,
                                                          full_path="/root")

        expected_dict = self.complex_type_data_handler.get_json(xsd_files)
        self.assertDictEqual(result_string, expected_dict)

    def test_create_complex_content_basic(self):
        xsd_files = join("complex_content", "basic")
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath("/xs:schema/xs:complexType", namespaces=self.namespaces)[0]

        result_string = self.parser.generate_complex_type(xsd_element, xsd_tree,
                                                          full_path="/root")

        expected_dict = self.complex_type_data_handler.get_json(xsd_files)
        self.assertDictEqual(result_string, expected_dict)

    def test_create_attribute_basic(self):
        xsd_files = join("attribute", "basic")
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath("/xs:schema/xs:complexType", namespaces=self.namespaces)[0]

        result_string = self.parser.generate_complex_type(xsd_element, xsd_tree,
                                                          full_path="/root")

        expected_dict = self.complex_type_data_handler.get_json(xsd_files)
        self.assertDictEqual(result_string, expected_dict)

    def test_create_multiple_basic(self):
        xsd_files = join("multiple", "basic")
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath("/xs:schema/xs:complexType", namespaces=self.namespaces)[0]

        result_string = self.parser.generate_complex_type(xsd_element, xsd_tree,
                                                          full_path="/root")

        expected_dict = self.complex_type_data_handler.get_json(xsd_files)
        self.assertDictEqual(result_string, expected_dict)


class ParserReloadComplexTypeTestSuite(TestCase):
    """ Element reload unit tests
    """

    def setUp(self):
        complex_type_data = join(RESOURCES_PATH, "parser", "complex_type")
        self.complex_type_data_handler = DataHandler(complex_type_data)

        # Set default namespace
        self.namespace = LXML_SCHEMA_NAMESPACE
        self.namespaces = {"xs": SCHEMA_NAMESPACE}

        # Get an instance of the XSDParser
        self.parser = XSDParser()
        self.parser.editing = True

    def test_reload_choice_basic(self):
        xsd_files = join("choice", "basic")
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath("/xs:schema/xs:complexType", namespaces=self.namespaces)[0]

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = XSDTree.tostring(xml_tree)
        edit_data_tree = XSDTree.transform_to_xml(xml_data)

        # Generate result dict
        result_string = self.parser.generate_complex_type(
            xsd_element, xsd_tree, full_path="/root", edit_data_tree=edit_data_tree
        )

        # Load expected dictionary and compare with result
        expected_dict = self.complex_type_data_handler.get_json("%s.reload" % xsd_files)
        self.assertDictEqual(result_string, expected_dict)

    def test_reload_sequence_basic(self):
        xsd_files = join("sequence", "basic")
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath("/xs:schema/xs:complexType", namespaces=self.namespaces)[0]

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = XSDTree.tostring(xml_tree)
        edit_data_tree = XSDTree.transform_to_xml(xml_data)

        # Generate result dict
        result_string = self.parser.generate_complex_type(
            xsd_element, xsd_tree, full_path="/root", edit_data_tree=edit_data_tree
        )

        # Load expected dictionary and compare with result
        expected_dict = self.complex_type_data_handler.get_json("%s.reload" % xsd_files)
        self.assertDictEqual(result_string, expected_dict)

    def test_reload_simple_content_basic(self):
        xsd_files = join("simple_content", "basic")
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath("/xs:schema/xs:complexType", namespaces=self.namespaces)[0]

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = XSDTree.tostring(xml_tree)
        edit_data_tree = XSDTree.transform_to_xml(xml_data)

        xml_value = xml_tree.xpath("/root", namespaces=self.namespaces)[0].text

        # Generate result dict
        result_string = self.parser.generate_complex_type(
            xsd_element, xsd_tree, full_path="/root", edit_data_tree=edit_data_tree,
            default_value=xml_value
        )

        # Load expected dictionary and compare with result
        expected_dict = self.complex_type_data_handler.get_json("%s.reload" % xsd_files)
        self.assertDictEqual(result_string, expected_dict)

    def test_reload_complex_content_basic(self):
        xsd_files = join("complex_content", "basic")
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath("/xs:schema/xs:complexType", namespaces=self.namespaces)[0]

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = XSDTree.tostring(xml_tree)
        edit_data_tree = XSDTree.transform_to_xml(xml_data)

        # Generate result dict
        result_string = self.parser.generate_complex_type(
            xsd_element, xsd_tree, full_path="/root", edit_data_tree=edit_data_tree
        )

        # Load expected dictionary and compare with result
        expected_dict = self.complex_type_data_handler.get_json("%s.reload" % xsd_files)
        self.assertDictEqual(result_string, expected_dict)

    def test_reload_attribute_basic(self):
        xsd_files = join("attribute", "basic")
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath("/xs:schema/xs:complexType", namespaces=self.namespaces)[0]

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = XSDTree.tostring(xml_tree)
        edit_data_tree = XSDTree.transform_to_xml(xml_data)

        # Generate result dict
        result_string = self.parser.generate_complex_type(
            xsd_element, xsd_tree, full_path="/root", edit_data_tree=edit_data_tree
        )

        # Load expected dictionary and compare with result
        expected_dict = self.complex_type_data_handler.get_json("%s.reload" % xsd_files)
        self.assertDictEqual(result_string, expected_dict)

    def test_reload_multiple_basic(self):
        xsd_files = join("multiple", "basic")
        xsd_tree = self.complex_type_data_handler.get_xsd(xsd_files)
        xsd_element = xsd_tree.xpath("/xs:schema/xs:complexType", namespaces=self.namespaces)[0]

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = XSDTree.tostring(xml_tree)
        edit_data_tree = XSDTree.transform_to_xml(xml_data)

        # Generate result dict
        result_string = self.parser.generate_complex_type(
            xsd_element, xsd_tree, full_path="/root", edit_data_tree=edit_data_tree
        )

        # Load expected dictionary and compare with result
        expected_dict = self.complex_type_data_handler.get_json("%s.reload" % xsd_files)
        self.assertDictEqual(result_string, expected_dict)
