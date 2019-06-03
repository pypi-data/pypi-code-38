""" XSD tree operation, build, parse
"""
from io import BytesIO

import lxml.etree as etree
from lxml.etree import Element, SubElement

import xml_utils.commons.constants as xml_constants
import xml_utils.commons.exceptions as exceptions


class XSDTree(object):
    """ XSD tree class
    """

    @staticmethod
    def build_tree(xml_string):
        """ Returns a lxml etree from an XML string (xml, xsd...)

        Args:
            xml_string:

        Returns:

        """
        try:
            xml_string = BytesIO(xml_string.encode('utf-8'))
        except Exception:
            xml_string = BytesIO(xml_string)

        return etree.parse(xml_string)

    @staticmethod
    def tostring(xml_tree, pretty=False):
        """ Return an XML String from a lxml etree

        Args:
            xml_tree:
            pretty:

        Returns:

        """
        try:
            return etree.tostring(xml_tree, pretty_print=pretty)
        except Exception as e:
            raise exceptions.XMLError(e.message)

    @staticmethod
    def transform_to_xslt(xml_parsed):
        """ Turn an XML document into an XSLT object.

        Args:
            xml_parsed:

        Returns:

        """
        try:
            return etree.XSLT(xml_parsed)
        except:
            return etree.XSLT(xml_parsed.encode('utf-8'))

    @staticmethod
    def transform_to_xml(xml_string):
        """ Turn an XML document into an XML object.

        Args:
            xml_string:

        Returns:

        """
        try:
            return etree.XML(xml_string)
        except:
            return etree.XML(xml_string.encode('utf-8'))

    @staticmethod
    def fromstring(xml_string, parser=None):
        """ Convert a string to an XML tree

        Args:
            xml_string:
            parser:

        Returns:

        """
        try:
            return etree.fromstring(xml_string, parser=parser)
        except Exception as e:
            raise exceptions.XMLError(e.message)

    @staticmethod
    def iterfind(xml_string, match):
        """ Finds all matching sub elements, by tag name or path.
        Args:
            xml_string: String xml.
            match: Pattern to match

        Returns:
            An iterable yielding all matching elements in document order.

        """
        try:
            xml_tree = XSDTree.build_tree(xml_string)
            return xml_tree.iterfind(match)
        except Exception as e:
            raise exceptions.XMLError(e.message)

    @staticmethod
    def iterparse(xml_string, events):
        """ Returns etree.iterparse

        Args:
            xml_string:
            events:

        Returns:

        """
        try:
            xml_file = BytesIO(xml_string.encode('utf-8'))
            return etree.iterparse(xml_file, events)
        except Exception as e:
            raise exceptions.XMLError(e.message)

    @staticmethod
    def get_extension(xml_tree):
        """ Returns the extension file from a parsed xml

        Args:
            xml_tree: result of build_tree

        Returns:

        """
        try:
            return xml_tree.find("//xsl:output",
                                 namespaces={'xsl': xml_constants.XSL_NAMESPACE}).attrib['method']
        except Exception as e:
            raise exceptions.XMLError(e.message)

    @staticmethod
    def create_element(tag, attrib=None, nsmap=None, **extra):
        """
        This function creates an Element.

        Args:
            tag:
            attrib:
            nsmap:
            extra:

        Returns:
        """
        return Element(tag, attrib, nsmap, **extra)

    @staticmethod
    def create_sub_element(parent, tag, attrib=None, nsmap=None, **extra):
        """
        This function creates a SubElement.

        Args:
            parent:
            tag:
            attrib:
            nsmap:
            extra:

        Returns:
        """
        return SubElement(parent, tag, attrib, nsmap, **extra)
