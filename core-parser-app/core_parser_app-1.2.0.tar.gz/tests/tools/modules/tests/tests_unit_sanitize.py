"""Sanitize unit testing
"""

from unittest.case import TestCase
from core_parser_app.tools.modules.sanitize import sanitize


class TestSanitize(TestCase):

    def test_sanitize_special_character_returns_encoded_character(self):
        self.assertEquals("&lt;", sanitize("<"))

    def test_sanitize_string_returns_string(self):
        self.assertEquals("test", sanitize("test"))

    def test_sanitize_int_returns_int(self):
        self.assertEquals(1, sanitize(1))

    def test_sanitize_float_returns_float(self):
        self.assertEquals(1.0, sanitize(1.0))

    def test_sanitize_xml_returns_encoded_xml(self):
        xml = "<root><element>value</element></root>"
        expected = "&lt;root&gt;&lt;element&gt;value&lt;/element&gt;&lt;/root&gt;"
        self.assertEquals(expected, sanitize(xml))

    def test_sanitize_bad_xml_returns_encoded_xml(self):
        xml = "<root<element>value</element></root>"
        expected = "&lt;root&lt;element&gt;value&lt;/element&gt;&lt;/root&gt;"
        self.assertEquals(expected, sanitize(xml))

    def test_sanitize_list_of_xml_returns_list_of_encoded_xml(self):
        xml = "<root><element>value</element></root>"
        expected = "&lt;root&gt;&lt;element&gt;value&lt;/element&gt;&lt;/root&gt;"
        xml_list = [xml, xml]
        expected_list = [expected, expected]
        self.assertEquals(expected_list, sanitize(xml_list))

    def test_sanitize_dict_of_xml_returns_dict_of_encoded_xml(self):
        xml = "<root><element>value</element></root>"
        expected = "&lt;root&gt;&lt;element&gt;value&lt;/element&gt;&lt;/root&gt;"
        xml_dict = {xml: xml}
        expected_dict = {expected: expected}
        self.assertEquals(expected_dict, sanitize(xml_dict))
