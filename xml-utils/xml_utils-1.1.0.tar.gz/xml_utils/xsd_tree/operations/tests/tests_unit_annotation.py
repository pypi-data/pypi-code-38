"""Unit tests for annotation operations
"""
from unittest import TestCase

from xml_utils.xsd_tree.operations.annotation import remove_annotations
from xml_utils.xsd_tree.xsd_tree import XSDTree


class TestRemoveAnnotations(TestCase):
    def test_remove_no_annotations_returns_same_value(self):
        xsd_string = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:element name="integer" type="xs:integer"/></xs:schema>'

        xsd_tree = XSDTree.build_tree(xsd_string)
        remove_annotations(xsd_tree)
        result_xsd_string = XSDTree.tostring(xsd_tree)

        self.assertTrue(xsd_string == result_xsd_string)

    def test_remove_annotations_returns_tree_without_annotations(self):
        xsd_string = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:annotation><xs:appinfo/></xs:annotation>' \
                     '<xs:element name="integer" type="xs:integer"/></xs:schema>'

        expected_xsd_string = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                              '<xs:element name="integer" type="xs:integer"/></xs:schema>'

        xsd_tree = XSDTree.build_tree(xsd_string)
        remove_annotations(xsd_tree)
        result_xsd_string = XSDTree.tostring(xsd_tree)

        self.assertTrue(expected_xsd_string == result_xsd_string)
