"""Unit tests for namespaces operations
"""
from unittest import TestCase
from lxml import etree
from xml_utils.xsd_tree.operations.namespaces import get_namespaces, get_default_prefix, get_target_namespace
from xml_utils.xsd_tree.xsd_tree import XSDTree


class TestGetNamespaces(TestCase):
    def test_get_namespaces_one_namespace_prefix_is_key(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'></xs:schema>"
        namespaces = get_namespaces(xsd_string)
        self.assertTrue('xs' in namespaces.keys())

    def test_get_namespaces_one_namespace_namespace_is_value(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'></xs:schema>"
        namespaces = get_namespaces(xsd_string)
        self.assertTrue(namespaces['xs'] == 'http://www.w3.org/2001/XMLSchema')

    def test_get_namespaces_two_namespaces(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema' xmlns:test='test'></xs:schema>"
        namespaces = get_namespaces(xsd_string)
        self.assertTrue('xs' in namespaces.keys() and 'test' in namespaces.keys())

    def test_get_namespaces_invalid_file(self):
        xsd_string = "invalid"
        with self.assertRaises(etree.XMLSyntaxError):
            get_namespaces(xsd_string)

    def test_get_namespaces_xml_namespace(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'></xs:schema>"
        namespaces = get_namespaces(xsd_string)
        self.assertTrue('xml' in namespaces.keys())


class TestGetDefautPrefix(TestCase):
    def test_get_xs_prefix(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'></xs:schema>"
        namespaces = get_namespaces(xsd_string)
        prefix = get_default_prefix(namespaces)
        self.assertTrue(prefix == 'xs')

    def test_get_xsd_prefix(self):
        xsd_string = "<xsd:schema xmlns:xsd='http://www.w3.org/2001/XMLSchema'></xsd:schema>"
        namespaces = get_namespaces(xsd_string)
        prefix = get_default_prefix(namespaces)
        self.assertTrue(prefix == 'xsd')

    def test_get_no_prefix(self):
        xsd_string = "<schema></schema>"
        namespaces = get_namespaces(xsd_string)
        prefix = get_default_prefix(namespaces)
        self.assertTrue(prefix == '')


class TestGetTargetNamespace(TestCase):
    def test_no_target_namespace_returns_none_values(self):
        xsd_string = "<schema></schema>"
        xsd_tree = XSDTree.build_tree(xsd_string)
        namespaces = get_namespaces(xsd_string)
        self.assertEquals((None, ''), get_target_namespace(xsd_tree, namespaces))

    def test_target_namespace_no_prefix_returns_target_namespace_only(self):
        xsd_string = "<schema targetNamespace='namespace'></schema>"
        xsd_tree = XSDTree.build_tree(xsd_string)
        namespaces = get_namespaces(xsd_string)
        self.assertEquals(('namespace', ''), get_target_namespace(xsd_tree, namespaces))

    def test_target_namespace_with_prefix_returns_target_namespace_and_prefix(self):
        xsd_string = "<schema targetNamespace='namespace' xmlns:ns='namespace'></schema>"
        xsd_tree = XSDTree.build_tree(xsd_string)
        namespaces = get_namespaces(xsd_string)
        self.assertEquals(('namespace', 'ns'), get_target_namespace(xsd_tree, namespaces))
