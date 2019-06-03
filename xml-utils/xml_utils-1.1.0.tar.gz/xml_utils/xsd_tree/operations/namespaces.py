"""XSD Tree operations on namespaces
"""
from xml_utils.commons import constants as xml_utils_constants
from xml_utils.xsd_tree.xsd_tree import XSDTree


def get_namespaces(xsd_string):
    """Returns dict of prefix and namespaces

    Args:
        xsd_string:

    Returns:

    """
    # events to look for during iterparse
    events = "start", "start-ns"
    # initialize namespaces dictionary
    namespaces = {'xml': xml_utils_constants.XML_NAMESPACE}
    # iterate file namespaces
    for event, elem in XSDTree.iterparse(xsd_string, events):
        if event == "start-ns":
            if len(elem[0]) > 0 and len(elem[1]) > 0:
                namespaces[elem[0]] = "%s" % elem[1]
        elif event == "start":
            break

    return namespaces


def get_default_prefix(namespaces):
    """Returns the default prefix used in the schema

    Args:
        namespaces:

    Returns:

    """
    default_prefix = ''
    for prefix, url in namespaces.items():
        if url == xml_utils_constants.SCHEMA_NAMESPACE:
            default_prefix = prefix
            break

    return default_prefix


def get_global_namespace(xsd_string):
    """ Get global namespace used in schema (defined by xmlns=<namespace>)

    Returns:

    """
    # events to look for during iterparse
    events = "start", "start-ns"
    # Initialize global namespace
    global_namespace = None
    # iterate file namespaces
    for event, elem in XSDTree.iterparse(xsd_string, events):
        if event == "start-ns":
            if len(elem[0]) == 0:
                global_namespace = elem[1]
        elif event == "start":
            break

    return global_namespace


def get_target_namespace(xsd_tree, namespaces):
    """Returns the target namespace used in the schema

    Args:
        xsd_tree:
        namespaces:

    Returns:

    """
    # get attributes of the root element (schema)
    root_attributes = xsd_tree.getroot().attrib
    # check if a target namespace is present
    target_namespace = root_attributes['targetNamespace'] if 'targetNamespace' in root_attributes else None
    # set default prefix to empty string
    target_namespace_prefix = ''
    # if a target namespace is present
    if target_namespace is not None:
        # iterate through namespaces
        for prefix, url in namespaces.items():
            # if an url matching the target namespace is found
            if url == target_namespace:
                # set the target namespace prefix with the associated prefix
                target_namespace_prefix = prefix
                # stop the search
                break

    # return target namespace and associated prefix
    return target_namespace, target_namespace_prefix
