""" Package computing the hash a XML string.
"""
import hashlib
import json
from collections import OrderedDict
from io import BytesIO

import six
import xmltodict
from lxml import etree

from xml_utils.xsd_tree.xsd_tree import XSDTree


def get_hash(xml_string):
    """ Get the hash of an XML String. Removes blank text, comments,
    processing instructions and annotations from the input. Allows to
    retrieve the same hash for two similar XML string.

    Args:
        xml_string (str): XML String to hash

    Returns:
        str: SHA-1 hash of the XML string
    """
    # Load the required parser
    hash_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    etree.set_default_parser(parser=hash_parser)

    xml_tree = XSDTree.build_tree(xml_string)

    # Remove all annotations
    annotations = xml_tree.findall(".//{http://www.w3.org/2001/XMLSchema}annotation")
    for annotation in annotations:
        annotation.getparent().remove(annotation)
    clean_xml_string = XSDTree.tostring(xml_tree)

    # Parse XML string into dict
    xml_dict = xmltodict.parse(clean_xml_string, dict_constructor=dict)
    # Returns the SHA-1 hash of the ordered dict
    return hash_dict(xml_dict)


def hash_dict(xml_dict):
    # Order dictionary by key
    xml_dict = OrderedDict(sorted(xml_dict.items(), key=lambda i: i[0]))

    # Hash dict according to value
    for xml_dict_key, xml_dict_val in xml_dict.items():
        if xml_dict_val is None:
            continue

        if type(xml_dict_val) is dict:
            xml_dict[xml_dict_key] = hash_dict(xml_dict_val)
        elif type(xml_dict_val) is list:
            xml_dict[xml_dict_key] = hash_list(xml_dict_val)
        elif not isinstance(xml_dict_val, six.string_types):
            raise TypeError("%s is not a type that we can hash" % type(xml_dict_val))

    # Extract string via JSON and compute SHA-1
    sorted_xml_string = json.dumps(xml_dict)
    return hashlib.sha1(sorted_xml_string.encode("utf-8")).hexdigest()


def hash_list(xml_list):
    xml_list_copy = list()

    for xml_list_val in xml_list:
        if type(xml_list_val) is dict:
            xml_list_copy.append(hash_dict(xml_list_val))
        elif isinstance(xml_list_val, six.string_types):
            xml_list_copy.append(xml_list_val)
        else:
            raise TypeError("%s is not a type that we can hash" % type(xml_list_val))

    # Sort list items and compute SHA-1
    sorted_xml_list = json.dumps(sorted(xml_list_copy))
    return hashlib.sha1(sorted_xml_list.encode("utf-8")).hexdigest()
