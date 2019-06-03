"""XSD Tree operations on attributes
"""
from xml_utils.xsd_tree.operations.namespaces import get_namespaces
from xml_utils.xsd_tree.operations.xpath import get_element_by_xpath
from xml_utils.xsd_tree.xsd_tree import XSDTree


def set_attribute(xsd_string, xpath, attribute, value):
    """Sets an attribute of an element

    Args:
        xsd_string:
        xpath:
        attribute:
        value:

    Returns:

    """
    return _update_attribute(xsd_string, xpath, attribute, value)


def delete_attribute(xsd_string, xpath, attribute):
    """Deletes an attribute from an element

    Args:
        xsd_string:
        xpath:
        attribute:

    Returns:

    """
    return _update_attribute(xsd_string, xpath, attribute)


def _update_attribute(xsd_string, xpath, attribute, value=None):
    """Updates an attribute (sets the value or deletes)

    Args:
        xsd_string:
        xpath: xpath of the element to update
        attribute: name of the attribute to update
        value: value of the attribute to set

    Returns:

    """
    # Build the XSD tree
    xsd_tree = XSDTree.build_tree(xsd_string)
    # Get namespaces
    namespaces = get_namespaces(xsd_string)
    # Get XSD element using its xpath
    element = get_element_by_xpath(xsd_tree, xpath, namespaces)

    # Add or update the attribute
    if value is not None:
        # Set element attribute with value
        element.attrib[attribute] = value
    else:
        # Deletes attribute
        if attribute in element.attrib:
            del element.attrib[attribute]

    # Converts XSD tree back to string
    updated_xsd_string = XSDTree.tostring(xsd_tree)

    return updated_xsd_string
