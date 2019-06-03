"""Unit tests for attributes operations
"""
from unittest import TestCase
from lxml import etree

from xml_utils.commons.exceptions import XMLError
from xml_utils.xsd_tree.operations.attribute import set_attribute, delete_attribute


class TestSetAttribute(TestCase):
    def test_set_attribute_invalid_xsd_raises_xsd_error(self):
        xsd_string = "invalid"
        with self.assertRaises(etree.XMLSyntaxError):
            set_attribute(xsd_string, "", "", "")

    def test_set_attribute_invalid_xpath_raises_xsd_error(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><root><test></test></root></xs:schema>"
        xpath = "invalid"
        with self.assertRaises(XMLError):
            set_attribute(xsd_string, xpath, "", "")

    def test_set_attribute_adds_attribute(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><root><test></test></root></xs:schema>"
        xpath = "root/test"
        attribute_name = "attr"
        updated_xsd_string = set_attribute(xsd_string, xpath, attribute_name, "")
        self.assertTrue('<test attr=' in updated_xsd_string)

    def test_set_attribute_adds_attribute_with_value(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><root><test></test></root></xs:schema>"
        xpath = "root/test"
        attribute_name = "attr"
        attribute_value = "value"
        updated_xsd_string = set_attribute(xsd_string, xpath, attribute_name, attribute_value)
        self.assertTrue('<test attr="value"' in updated_xsd_string)

    def test_set_attribute_if_present(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>" \
                     "<root><test attr='old'></test></root></xs:schema>"
        xpath = "root/test"
        attribute_name = "attr"
        attribute_value = "new"
        updated_xsd_string = set_attribute(xsd_string, xpath, attribute_name, attribute_value)
        self.assertTrue('<test attr="new"' in updated_xsd_string)


class TestDeleteAttribute(TestCase):
    def test_delete_attribute_invalid_xsd_raises_xsd_error(self):
        xsd_string = "invalid"
        with self.assertRaises(etree.XMLSyntaxError):
            delete_attribute(xsd_string, "", "")

    def test_delete_attribute_invalid_xpath_raises_xsd_error(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><root><test></test></root></xs:schema>"
        xpath = "invalid"
        with self.assertRaises(XMLError):
            delete_attribute(xsd_string, xpath, "")

    def test_delete_attribute_removed_if_exists(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>" \
                     "<root><test attr='value'></test></root></xs:schema>"
        xpath = "root/test"
        attribute_name = "attr"
        updated_xsd_string = delete_attribute(xsd_string, xpath, attribute_name)
        self.assertTrue('attr=' not in updated_xsd_string)

    def test_delete_attribute_does_not_fail_if_not_present(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>" \
                     "<root><test></test></root></xs:schema>"
        xpath = "root/test"
        attribute_name = "attr"
        delete_attribute(xsd_string, xpath, attribute_name)
