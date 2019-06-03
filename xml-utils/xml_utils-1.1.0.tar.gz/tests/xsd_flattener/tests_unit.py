from os.path import join, dirname
from unittest import TestCase
from mock.mock import patch
from xml_utils.xsd_flattener.xsd_flattener_url import XSDFlattenerURL


RESOURCES_PATH = join(dirname(__file__), 'data')


class TestXSDFlattener(TestCase):

    def test_no_include_returns_same_content(self):
        xml_string = '<schema xmlns="http://www.w3.org/2001/XMLSchema"/>'
        flattener = XSDFlattenerURL(xml_string)
        flat_string = flattener.get_flat()
        self.assertEquals(xml_string, flat_string)

    @patch('xml_utils.xsd_flattener.xsd_flattener_url.XSDFlattenerURL.get_dependency_content')
    def test_one_include_returns_flat_content(self, mock_get_dependency_content):
        xml_string = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:include schemaLocation="test.xsd"/></xs:schema>'

        dependency = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:element name="test"/></xs:schema>'

        flattener = XSDFlattenerURL(xml_string)
        mock_get_dependency_content.return_value = dependency
        flat_string = flattener.get_flat()
        self.assertTrue('<xs:element name="test"/>' in flat_string)

    @patch('xml_utils.xsd_flattener.xsd_flattener_url.XSDFlattenerURL.get_dependency_content')
    def test_one_include_removes_include(self, mock_get_dependency_content):
        xml_string = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:include schemaLocation="test.xsd"/></xs:schema>'

        dependency = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:element name="test"/></xs:schema>'

        flattener = XSDFlattenerURL(xml_string)
        mock_get_dependency_content.return_value = dependency
        flat_string = flattener.get_flat()
        self.assertTrue('<xs:include schemaLocation="test.xsd"/>' not in flat_string)

    @patch('xml_utils.xsd_flattener.xsd_flattener_url.XSDFlattenerURL.get_dependency_content')
    def test_two_identical_includes_returns_flat_content(self, mock_get_dependency_content):
        xml_string = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:include schemaLocation="test.xsd"/><xs:include schemaLocation="test.xsd"/>' \
                     '</xs:schema>'

        dependency = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:element name="test"/></xs:schema>'

        flattener = XSDFlattenerURL(xml_string)
        mock_get_dependency_content.return_value = dependency
        flat_string = flattener.get_flat()
        self.assertTrue('<xs:element name="test"/>' in flat_string)

    @patch('xml_utils.xsd_flattener.xsd_flattener_url.XSDFlattenerURL.get_dependency_content')
    def test_two_identical_includes_removes_two_includes(self, mock_get_dependency_content):
        xml_string = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:include schemaLocation="test.xsd"/><xs:include schemaLocation="test.xsd"/>' \
                     '</xs:schema>'

        dependency = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:element name="test"/></xs:schema>'

        flattener = XSDFlattenerURL(xml_string)
        mock_get_dependency_content.return_value = dependency
        flat_string = flattener.get_flat()
        self.assertTrue('<xs:include schemaLocation="test.xsd"/>' not in flat_string)

    @patch('xml_utils.xsd_flattener.xsd_flattener_url.XSDFlattenerURL.get_dependency_content')
    def test_two_identical_includes_replaces_two_includes_by_their_content(self, mock_get_dependency_content):
        xml_string = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:include schemaLocation="test1.xsd"/><xs:include schemaLocation="test2.xsd"/>' \
                     '</xs:schema>'

        dependency_1 = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                       '<xs:element name="test1"/></xs:schema>'
        dependency_2 = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                       '<xs:element name="test2"/></xs:schema>'

        flattener = XSDFlattenerURL(xml_string)
        mock_get_dependency_content.side_effect = [dependency_1, dependency_2]
        flat_string = flattener.get_flat()
        # assert that no more includes are present in the file
        self.assertTrue('include' not in flat_string)
        # assert that dependencies' contents are in the file
        self.assertTrue('<xs:element name="test1"/>' in flat_string)
        self.assertTrue('<xs:element name="test2"/>' in flat_string)
