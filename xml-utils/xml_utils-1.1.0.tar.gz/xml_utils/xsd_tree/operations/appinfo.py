"""XSD Tree operations on appinfo
"""
from xml_utils.commons.exceptions import XMLError
from xml_utils.xsd_tree.operations.namespaces import get_namespaces
from xml_utils.xsd_tree.operations.xpath import get_element_by_xpath
from xml_utils.xsd_tree.xsd_tree import XSDTree
from xml_utils.commons import constants as xml_utils_constants
from lxml import etree


def add_appinfo_element(xsd_string, xpath, appinfo_name, value):
    """Adds appinfo to an element

    Args:
        xsd_string:
        xpath:
        appinfo_name:
        value:

    Returns:

    """
    return _update_appinfo_element(xsd_string, xpath, appinfo_name, value)


def delete_appinfo_element(xsd_string, xpath, attribute_name):
    """Deletes appinfo from an element

    Args:
        xsd_string:
        xpath:
        attribute_name:

    Returns:

    """
    return _update_appinfo_element(xsd_string, xpath, attribute_name)


def _get_appinfo_element(element, element_name, namespace):
    """Get an element from the appinfo

    Args:
        element:
        element_name:
        namespace:

    Returns:

    """
    element_name_any_namespace = "{*}" + element_name
    appinfo_elements = element.findall("./{0}annotation/{0}appinfo/{1}".format(namespace, element_name_any_namespace))

    if len(appinfo_elements) == 1:
        return appinfo_elements[0]
    elif len(appinfo_elements) > 1:
        raise XMLError("{} appinfo found multiple times in the same element".format(element_name))
    elif len(appinfo_elements) == 0:
        return None


def _update_appinfo_element(xsd_string, xpath, appinfo_name, value=None):
    """Updates an appinfo element

    Args:
        xsd_string:
        xpath: xpath to element to update
        appinfo_name: name of the attribute to update
        value: value to set

    Returns:

    """
    # Build the XSD tree
    xsd_tree = XSDTree.build_tree(xsd_string)
    # Get namespaces
    namespaces = get_namespaces(xsd_string)
    # Get XSD element using its xpath
    element = get_element_by_xpath(xsd_tree, xpath, namespaces)

    if value is not None:
        # If a value is provided, create or update the appinfo
        add_appinfo_child_to_element(element, appinfo_name, value)
    else:
        # value is None, deletes the appinfo if present
        delete_appinfo_child_from_element(element, appinfo_name)

    # Converts XSD tree back to string
    updated_xsd_string = XSDTree.tostring(xsd_tree)

    return updated_xsd_string


def add_appinfo_child_to_element(element, appinfo_name, value):
    """Adds an appinfo child to an etree element

    Args:
        element:
        appinfo_name:
        value:

    Returns:

    """
    # Get the appinfo element
    appinfo_element = _get_appinfo_element(element, appinfo_name, xml_utils_constants.LXML_SCHEMA_NAMESPACE)

    # if appinfo is absent, creates it
    if appinfo_element is None:
        # get annotation tag
        annotation = _get_or_create_element(element, "annotation", xml_utils_constants.LXML_SCHEMA_NAMESPACE)

        # get appinfo tag
        appinfo = _get_or_create_element(annotation, "appinfo", xml_utils_constants.LXML_SCHEMA_NAMESPACE)

        # get attribute tag
        appinfo_element = _get_or_create_element(appinfo, appinfo_name)

    # set the value of the appinfo
    appinfo_element.text = value


def delete_appinfo_child_from_element(element, appinfo_name):
    """Deletes an appinfo child an etree element

    Args:
        element:
        appinfo_name: name of the appinfo to delete

    Returns:

    """
    # Get the appinfo element
    appinfo_element = _get_appinfo_element(element, appinfo_name, xml_utils_constants.LXML_SCHEMA_NAMESPACE)

    # if appinfo is present, deletes it
    if appinfo_element is not None:
        appinfo_element.getparent().remove(appinfo_element)


def _get_or_create_element(parent, element_tag, namespace=""):
    """Gets an element in children or creates it

    Args:
        parent:
        element_tag:
        namespace:

    Returns:

    """
    element = parent.find("./{0}{1}".format(namespace, element_tag))
    if element is None:
        # create element if absent
        element = etree.Element("{0}{1}".format(namespace, element_tag))
        # insert element
        parent.insert(0, element)

    return element
