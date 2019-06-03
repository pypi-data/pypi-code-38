"""XSD Tree operations on xpath
"""
from xml_utils.commons import constants as xml_utils_constants
from xml_utils.commons.exceptions import XMLError
from xml_utils.xsd_tree.operations.namespaces import get_default_prefix


def get_element_by_xpath(xsd_tree, xpath, namespaces=None):
    """Returns an element from its xpath

    Args:
        xsd_tree:
        xpath:
        namespaces:

    Returns:

    """
    if namespaces is not None:
        # Get default prefix
        default_prefix = get_default_prefix(namespaces)

        # Transform xpath into LXML format
        xpath = xpath.replace(default_prefix + ":", xml_utils_constants.LXML_SCHEMA_NAMESPACE)

    try:
        element = xsd_tree.find(xpath)
    except:
        raise XMLError('Unable to find an element for the given Xpath.')

    if element is not None:
        return element
    else:
        raise XMLError('Unable to find an element for the given Xpath.')
