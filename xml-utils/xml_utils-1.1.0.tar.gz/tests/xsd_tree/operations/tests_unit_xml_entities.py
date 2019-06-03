"""Unit tests for XmlEntities operation
"""
from unittest import TestCase

from xml_utils.xsd_tree.operations.xml_entities import XmlEntities


class TestEscapeXmlEntities(TestCase):
    def test_escape_with_predefined_xml_entities(self):
        string = 'aaa<bbb>ccc&ddd\'eee"fff'

        xmlEntities = XmlEntities()

        self.assertTrue(xmlEntities.escape_xml_entities(string) == 'aaa&lt;bbb&gt;ccc&amp;ddd&apos;eee&quot;fff')
        self.assertTrue(xmlEntities.unescaped_xml_string == string)
        self.assertTrue(xmlEntities.number_of_subs_made == 5)


    def test_escape_already_escaped_string(self):
        string = 'aaa&lt;bbb&gt;ccc&amp;ddd&apos;eee&quot;fff'

        xmlEntities = XmlEntities()

        self.assertTrue(xmlEntities.escape_xml_entities(string) == string)
        self.assertTrue(xmlEntities.unescaped_xml_string == string)
        self.assertTrue(xmlEntities.number_of_subs_made == 0)


    def test_escape_full_predefined_xml_entities(self):
        string = '<<<""\'\'\'\'\'\'\'""">>>'

        xmlEntities = XmlEntities()

        self.assertTrue(xmlEntities.escape_xml_entities(string) == '&lt;&lt;&lt;&quot;&quot;&apos;&apos;&apos;&apos;&apos;&apos;&apos;&quot;&quot;&quot;&gt;&gt;&gt;')
        self.assertTrue(xmlEntities.unescaped_xml_string == string)
        self.assertTrue(xmlEntities.number_of_subs_made == 18)

    def test_unescaped_and_already_escaped_predefined_xml_entities(self):
        string = '<&lt;&quot;>&&&lt;'

        xmlEntities = XmlEntities()

        self.assertTrue(xmlEntities.escape_xml_entities(string) == '&lt;&lt;&quot;&gt;&amp;&amp;&lt;')
        self.assertTrue(xmlEntities.unescaped_xml_string == string)
        self.assertTrue(xmlEntities.number_of_subs_made == 4)