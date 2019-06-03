# coding: utf-8
""" Unit tests for additional methods """
from unittest import TestCase

from xml_utils.commons.exceptions import XMLError
from xml_utils.xsd_tree.xsd_tree import XSDTree


class TestAdditionalMethods(TestCase):

    def test_iterparse_method_without_unicode(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><root><test></test></root></xs:schema>"
        XSDTree.iterparse(xsd_string, ('end',))

    def test_iterparse_method_with_unicode(self):
        xsd_string = u"<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><\u0192-root><test></test></\u0192-root></xs:schema>"
        XSDTree.iterparse(xsd_string, ('end',))

    def test_iterparse_method_without_decoded_symbols(self):
        xsd_string = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><ƒ-root><test></test></ƒ-root></xs:schema>"

        with self.assertRaises(XMLError):
            XSDTree.iterparse(xsd_string, ('end',))
