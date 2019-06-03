"""Unit tests for xpath operations
"""
from unittest import TestCase
from xml_utils.commons.exceptions import XMLError
from xml_utils.xsd_tree.operations.namespaces import get_namespaces
from xml_utils.xsd_tree.operations.xpath import get_element_by_xpath
from xml_utils.xsd_tree.xsd_tree import XSDTree


class TestGetElementByXpath(TestCase):
    def test_get_element_xpath_matching_element(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><root><test></test></root></xs:schema>"
        xpath = "root/test"
        xsd_tree = XSDTree.build_tree(xsd_string)
        element = get_element_by_xpath(xsd_tree, xpath)
        self.assertTrue(element is not None)

    def test_get_element_xpath_matching_element_with_xs_namespace_prefix(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><xs:element><xs:complexType>" \
                     "</xs:complexType></xs:element></xs:schema>"
        xpath = "xs:element/xs:complexType"
        xsd_tree = XSDTree.build_tree(xsd_string)
        namespaces = get_namespaces(xsd_string)
        element = get_element_by_xpath(xsd_tree, xpath, namespaces)
        self.assertTrue(element is not None)

    def test_get_element_xpath_matching_element_with_xsd_namespace_prefix(self):
        xsd_string = "<xsd:schema xmlns:xsd='http://www.w3.org/2001/XMLSchema'><xsd:element><xsd:complexType>" \
                     "</xsd:complexType></xsd:element></xsd:schema>"
        xpath = "xsd:element/xsd:complexType"
        xsd_tree = XSDTree.build_tree(xsd_string)
        namespaces = get_namespaces(xsd_string)
        element = get_element_by_xpath(xsd_tree, xpath, namespaces)
        self.assertTrue(element is not None)

    def test_get_element_xpath_not_matching_element_with_different_namespace_prefix(self):
        xsd_string = "<xsd:schema xmlns:xsd='http://www.w3.org/2001/XMLSchema'><xsd:element><xsd:complexType>" \
                     "</xsd:complexType></xsd:element></xsd:schema>"
        xpath = "xs:element/xs:complexType"
        xsd_tree = XSDTree.build_tree(xsd_string)
        namespaces = get_namespaces(xsd_string)
        with self.assertRaises(XMLError):
            get_element_by_xpath(xsd_tree, xpath, namespaces)

    def test_get_element_xpath_not_matching_element_without_namespace_prefix(self):
        xsd_string = "<xsd:schema xmlns:xsd='http://www.w3.org/2001/XMLSchema'><xsd:element><xsd:complexType>" \
                     "</xsd:complexType></xsd:element></xsd:schema>"
        xpath = "element/complexType"
        xsd_tree = XSDTree.build_tree(xsd_string)
        namespaces = get_namespaces(xsd_string)
        with self.assertRaises(XMLError):
            get_element_by_xpath(xsd_tree, xpath, namespaces)

    def test_get_element_xpath_not_matching_element(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><root><test></test></root></xs:schema>"
        xpath = "root/name"
        xsd_tree = XSDTree.build_tree(xsd_string)
        with self.assertRaises(XMLError):
            get_element_by_xpath(xsd_tree, xpath)

    def test_get_element_invalid_xpath(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><root><test></test></root></xs:schema>"
        xpath = "invalid"
        xsd_tree = XSDTree.build_tree(xsd_string)
        with self.assertRaises(XMLError):
            get_element_by_xpath(xsd_tree, xpath)
