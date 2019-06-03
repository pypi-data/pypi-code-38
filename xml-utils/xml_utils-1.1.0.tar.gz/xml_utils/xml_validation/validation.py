"""
    Api for XSD and XML validation using xerces server or lxml library
"""

import json

from lxml import etree

from xml_utils.xsd_tree.xsd_tree import XSDTree
from .xerces.client import send_message


def xerces_validate_xsd(xsd_tree):
    """  Send XML Schema to server to be validated

    Args:
        xsd_tree:

    Returns:
        None if no errors, string otherwise

    """
    xsd_string = _xsd_serialize(xsd_tree)
    message = {'xsd_string': xsd_string}
    message = _json_serialize(message)
    return send_message(message)


def xerces_validate_xml(xsd_tree, xml_tree):
    """ Send XML Data and XML Schema to server to validate data against the schema

    Args:
        xsd_tree:
        xml_tree:

    Returns:
        None if no errors, string otherwise

    """
    pretty_xml_string = _xsd_serialize(xml_tree, pretty_print=True)
    xsd_string = _xsd_serialize(xsd_tree)
    message = {'xsd_string': xsd_string, 'xml_string': pretty_xml_string}
    message = _json_serialize(message)
    return send_message(message)


def lxml_validate_xsd(xsd_tree, uri_resolver=None):
    """ Validate schema using LXML

    Args:
        xsd_tree:
        uri_resolver:

    Returns:
        errors

    """
    error = None
    try:
        _build_etree_schema(xsd_tree, uri_resolver)
    except Exception, e:
        error = e.message
    return error


def lxml_validate_xml(xsd_tree, xml_tree, uri_resolver=None):
    """ Validate document using LXML

    Args:
        xsd_tree:
        xml_tree:
        uri_resolver:

    Returns:
        errors

    """
    error = None
    try:
        xml_schema = _build_etree_schema(xsd_tree, uri_resolver)
        xml_schema.assertValid(xml_tree)
    except Exception, e:
        error = e.message
    return error


def _xsd_serialize(xsd_tree, pretty_print=False):
    """ Serialize xsd document

    Args:
        xsd_tree:
        pretty_print:

    Returns:
        xsd string

    """
    try:
        xsd_string = XSDTree.tostring(xsd_tree, pretty=pretty_print)
    except Exception as e:
        raise Exception("XSD serialization error : " + e.message)
    return xsd_string


def _json_serialize(message):
    """ Serialize json document

    Args:
        message:

    Returns:
        json string

    """
    try:
        message = json.dumps(message)
    except Exception as e:
        raise Exception("JSON serialization error : " + e.message)
    return message


def _build_etree_schema(xsd_tree, uri_resolver=None):
    """ Build an lxml etree XMLSchema

    Args:
        xsd_tree:
        uri_resolver:

    Returns:

    """
    if uri_resolver:
        xsd_tree.parser.resolvers.add(uri_resolver)
    xml_schema = etree.XMLSchema(xsd_tree)
    return xml_schema
