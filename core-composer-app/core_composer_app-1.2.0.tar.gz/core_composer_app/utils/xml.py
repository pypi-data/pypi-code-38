"""XML utils for Composer app
"""
from core_main_app.commons.exceptions import CoreError, XMLError
from core_main_app.utils.xml import is_well_formed_xml, validate_xml_schema

from xml_utils.commons.constants import LXML_SCHEMA_NAMESPACE
from xml_utils.xsd_tree.operations.namespaces import get_namespaces, get_default_prefix, get_target_namespace
from xml_utils.xsd_tree.xsd_tree import XSDTree

COMPLEX_TYPE = 'complexType'
SIMPLE_TYPE = 'simpleType'


def check_type_core_support(xsd_string):
    """Check that the format of the the type is supported by the current version of the Core.
    Return the type definition (simpleType or complexType).

    Args:
        xsd_string:

    Returns:
        type_definition: simpleType or complexType.

    """
    type_definition = ""
    error_message = "A type should be a valid XML schema containing only one type definition " \
                    "(Allowed tags are: simpleType or complexType and include)."

    # check that well formatted first
    if not is_well_formed_xml(xsd_string):
        raise XMLError('Uploaded file is not well formatted XML.')

    # build the tree
    xsd_tree = XSDTree.build_tree(xsd_string)

    # get elements
    elements = xsd_tree.findall("*")

    if len(elements) > 0:
        # only simpleType, complexType or include
        for element in elements:
            if 'complexType' not in element.tag \
                    and 'simpleType' not in element.tag \
                    and 'include' not in element.tag:
                raise CoreError(error_message)

        # only one type
        cpt_type = 0
        for element in elements:
            if 'complexType' in element.tag or 'simpleType' in element.tag:
                cpt_type += 1
                if cpt_type > 1:
                    raise CoreError(error_message)
                type_definition = COMPLEX_TYPE if 'complexType' in element.tag else SIMPLE_TYPE
    else:
        raise CoreError(error_message)

    return type_definition


def remove_single_root_element(xsd_string):
    """Remove root element from the xsd string.

    Args:
        xsd_string:

    Returns:

    """
    # Build xsd tree
    xsd_tree = XSDTree.build_tree(xsd_string)
    # find the root element
    root = xsd_tree.find("{}element".format(LXML_SCHEMA_NAMESPACE))
    if root is not None:
        # remove root element from parent (schema)
        root.getparent().remove(root)
        # convert the tree to back string
        xsd_string = XSDTree.tostring(xsd_tree)
    # return xsd string
    return xsd_string


def rename_single_root_type(xsd_string, type_name):
    """Rename the type of the single root element.

    Args:
        xsd_string:
        type_name:

    Returns:

    """
    # build xsd tree
    xsd_tree = XSDTree.build_tree(xsd_string)
    # xpath to the single root element
    xpath_root = LXML_SCHEMA_NAMESPACE + "element"
    # xpath to the single root type
    xpath_root_type = LXML_SCHEMA_NAMESPACE + "complexType"
    # change the root type name in the xsd tree
    xsd_tree.find(xpath_root).attrib['type'] = type_name
    xsd_tree.find(xpath_root_type).attrib['name'] = type_name
    # rebuild xsd string
    xsd_string = XSDTree.tostring(xsd_tree)
    # return xsd string
    return xsd_string


def delete_xsd_element(xsd_string, xpath):
    """Delete element from tree.

    Args:
        xsd_string:
        xpath:

    Returns:

    """
    # build xsd tree
    xsd_tree = XSDTree.build_tree(xsd_string)
    # get xsd namespaces
    namespaces = get_namespaces(xsd_string)
    # get default prefix
    default_prefix = get_default_prefix(namespaces)
    # set the element namespace
    xpath = xpath.replace(default_prefix + ":", LXML_SCHEMA_NAMESPACE)
    # get element to remove from tree
    element_to_remove = xsd_tree.find(xpath)
    # remove element from tree
    element_to_remove.getparent().remove(element_to_remove)

    # rebuild xsd string
    xsd_string = XSDTree.tostring(xsd_tree)
    # return xsd string
    return xsd_string


def change_xsd_element_type(xsd_string, xpath, type_name):
    """Change the type of an element (e.g. sequence -> choice).

    Args:
        xsd_string:
        xpath:
        type_name:

    Returns:

    """
    xsd_tree = XSDTree.build_tree(xsd_string)
    namespaces = get_namespaces(xsd_string)
    default_prefix = get_default_prefix(namespaces)

    # set the element namespace
    xpath = xpath.replace(default_prefix + ":", LXML_SCHEMA_NAMESPACE)
    xsd_tree.find(xpath).tag = LXML_SCHEMA_NAMESPACE + type_name

    # rebuild xsd string
    xsd_string = XSDTree.tostring(xsd_tree)

    # return xsd string
    return xsd_string


def set_xsd_element_occurrences(xsd_string, xpath, min_occurs, max_occurs):
    """Set occurrences of element.

    Args:
        xsd_string:
        xpath:
        min_occurs:
        max_occurs:

    Returns:

    """
    # build xsd tree
    xsd_tree = XSDTree.build_tree(xsd_string)
    # get namespaces
    namespaces = get_namespaces(xsd_string)
    # get default prefix
    default_prefix = get_default_prefix(namespaces)

    # set the element namespace
    xpath = xpath.replace(default_prefix + ":", LXML_SCHEMA_NAMESPACE)
    # add the element to the sequence
    element = xsd_tree.find(xpath)
    element.attrib['minOccurs'] = min_occurs
    element.attrib['maxOccurs'] = max_occurs

    # save the tree in the session
    xsd_string = XSDTree.tostring(xsd_tree)

    # return xsd string
    return xsd_string


def get_xsd_element_occurrences(xsd_string, xpath):
    """Get the min and max occurrences of the element.

    Args:
        xsd_string:
        xpath:

    Returns:

    """
    # build the xsd tree
    xsd_tree = XSDTree.build_tree(xsd_string)
    # get the namespaces
    namespaces = get_namespaces(xsd_string)
    # get the default prefix
    default_prefix = get_default_prefix(namespaces)

    # set the element namespace
    xpath = xpath.replace(default_prefix + ":", LXML_SCHEMA_NAMESPACE)
    # add the element to the sequence
    element = xsd_tree.find(xpath)

    if 'minOccurs' in element.attrib:
        min_occurs = element.attrib['minOccurs']
    else:
        min_occurs = "1"
    if 'maxOccurs' in element.attrib:
        max_occurs = element.attrib['maxOccurs']
    else:
        max_occurs = "1"

    return min_occurs, max_occurs


def rename_xsd_element(xsd_string, xpath, new_name):
    """Rename xsd element.

    Args:
        xsd_string:
        xpath:
        new_name:

    Returns:

    """
    # build the xsd tree
    xsd_tree = XSDTree.build_tree(xsd_string)
    # get the namespaces
    namespaces = get_namespaces(xsd_string)
    # get the default prefix
    default_prefix = get_default_prefix(namespaces)

    # set the element namespace
    xpath = xpath.replace(default_prefix + ":", LXML_SCHEMA_NAMESPACE)
    # rename element
    xsd_tree.find(xpath).attrib['name'] = new_name

    # rebuild xsd string
    xsd_string = XSDTree.tostring(xsd_tree)
    # return xsd string
    return xsd_string


# TODO: refactor more
def _insert_element_type(xsd_string, xpath, type_content, element_type_name, include_url):
    """Insert an element of given type in xsd string.

    Args:
        xsd_string: xsd string
        xpath: xpath where to insert the element
        type_content: string content of the type to insert
        element_type_name: name of the type
        include_url: url used to reference the type in schemaLocation

    Returns:

    """
    # build the dom tree of the schema being built
    xsd_tree = XSDTree.build_tree(xsd_string)
    # get namespaces information for the schema
    namespaces = get_namespaces(xsd_string)
    # get the default namespace
    default_prefix = get_default_prefix(namespaces)
    # get target namespace information
    target_namespace, target_namespace_prefix = get_target_namespace(xsd_tree, namespaces)
    # build xpath to element
    xpath = xpath.replace(default_prefix + ":", LXML_SCHEMA_NAMESPACE)
    # build xsd tree
    type_xsd_tree = XSDTree.build_tree(type_content)
    # get namespaces information for the type
    type_namespaces = get_namespaces(type_content)
    # get target namespace information
    type_target_namespace, type_target_namespace_prefix = get_target_namespace(type_xsd_tree, type_namespaces)

    # get the type from the included/imported file
    # If there is a complex type
    element_type = type_xsd_tree.find("{}complexType".format(LXML_SCHEMA_NAMESPACE))
    if element_type is None:
        # If there is a simple type
        element_type = type_xsd_tree.find("{}simpleType".format(LXML_SCHEMA_NAMESPACE))
    type_name = element_type.attrib["name"]

    # format type name to avoid forbidden xml characters
    element_type_name = _get_valid_xml_name(element_type_name)

    # variable that indicates if namespaces map needs to be updated
    update_ns_map = False

    # Schema without target namespace
    if target_namespace is None:
        # Type without target namespace
        if type_target_namespace is None:
            # create type name with namespace
            ns_type_name = type_name
            # create include element
            dependency_tag = 'include'
            dependency_attrib = {'schemaLocation': include_url}
        # Type with target namespace
        else:
            # create type name with namespace
            ns_type_name = _get_ns_type_name(type_target_namespace_prefix, type_name, prefix_required=True)
            # create import element
            dependency_tag = 'import'
            dependency_attrib = {'schemaLocation': include_url, 'namespace': type_target_namespace}
            update_ns_map = True

    # Schema with target namespace
    else:
        # Type without target namespace
        if type_target_namespace is None:
            # create type name with namespace
            ns_type_name = _get_ns_type_name(target_namespace_prefix, type_name)
            # create include element
            dependency_tag = 'include'
            dependency_attrib = {'schemaLocation': include_url}
        # Type with target namespace
        else:
            # Same target namespace as base template
            if target_namespace == type_target_namespace:
                # create type name with namespace
                ns_type_name = _get_ns_type_name(target_namespace_prefix, type_name)
                # create include element
                dependency_tag = 'include'
                dependency_attrib = {'schemaLocation': include_url}
            # Different target namespace as base template
            else:
                # create type name with namespace
                ns_type_name = _get_ns_type_name(type_target_namespace_prefix, type_name, prefix_required=True)
                # create import element
                dependency_tag = 'import'
                dependency_attrib = {'schemaLocation': include_url, 'namespace': type_target_namespace}
                update_ns_map = True

    # create dependency element
    dependency_element = _create_xsd_element(dependency_tag, dependency_attrib)
    # create xsd element
    xsd_element = _create_xsd_element('element', attrib={'name': element_type_name, 'type': ns_type_name})
    # check if dependency element (include/import) is already present
    dependency_tag = "{0}[@schemaLocation='{1}']".format(dependency_element.tag,
                                                         dependency_element.attrib['schemaLocation'])
    dependency_present = xsd_tree.find(dependency_tag) is not None

    if not dependency_present:
        # add dependency element (include/import)
        xsd_tree.getroot().insert(0, dependency_element)

    # add xsd element
    xsd_tree.find(xpath).append(xsd_element)

    # if namespace map of the schema needs to be updated
    if not dependency_present and update_ns_map:
        root = xsd_tree.getroot()
        root_ns_map = root.nsmap

        if type_target_namespace_prefix in root_ns_map.keys() and \
                        root_ns_map[type_target_namespace_prefix] != type_target_namespace:
            raise CoreError('The namespace prefix is already declared for a different namespace.')
        else:
            root_ns_map[type_target_namespace_prefix] = type_target_namespace
            new_root = XSDTree.create_element(root.tag, nsmap=root_ns_map, attrib=root.attrib)
            new_root[:] = root[:]

            # return result tree
            return new_root

    else:
        # return result tree
        return xsd_tree


def insert_element_type(xsd_string, xpath, type_content, element_type_name, include_url):
    """Insert an element of given type in xsd string, and validates result.

    Args:
        xsd_string: xsd string
        xpath: xpath where to insert the element
        type_content: string content of the type to insert
        element_type_name: name of the type
        include_url: url used to reference the type in schemaLocation

    Returns:

    """

    new_xsd_tree = _insert_element_type(xsd_string, xpath, type_content, element_type_name, include_url)

    error = validate_xml_schema(new_xsd_tree)

    # if errors, raise exception
    if error is not None:
        raise XMLError(error)

    new_xsd_string = XSDTree.tostring(new_xsd_tree)

    return new_xsd_string


def insert_element_built_in_type(xsd_string, xpath, element_type_name):
    """Insert element with a builtin type in xsd string.

    Args:
        xsd_string: xsd string
        xpath: xpath where to insert the element
        element_type_name: name of the type to insert

    Returns:

    """
    # build the dom tree of the schema being built
    xsd_tree = XSDTree.build_tree(xsd_string)
    # get namespaces information for the schema
    namespaces = get_namespaces(xsd_string)
    # get the default namespace
    default_prefix = get_default_prefix(namespaces)
    # build xpath to element
    xpath = xpath.replace(default_prefix + ":", LXML_SCHEMA_NAMESPACE)

    type_name = default_prefix + ':' + element_type_name
    xsd_tree.find(xpath).append(XSDTree.create_element("{}element".format(LXML_SCHEMA_NAMESPACE),
                                                       attrib={'type': type_name,
                                                               'name': element_type_name}))
    # validate XML schema
    error = validate_xml_schema(xsd_tree)

    # if errors, raise exception
    if error is not None:
        raise XMLError(error)

    return XSDTree.tostring(xsd_tree)


def _get_ns_type_name(prefix, type_name, prefix_required=False):
    """Return type name formatted with namespace prefix.

    Args:
        prefix:
        type_name:

    Returns:

    """
    if prefix != '':
        ns_type_name = "{0}:{1}".format(prefix, type_name)
    else:
        if not prefix_required:
            ns_type_name = type_name
        else:
            raise CoreError("Unable to add the type because no prefix is defined for the target namespace.")

    return ns_type_name


def _get_valid_xml_name(name):
    """Return a valid xml name.

    Args:
        name:

    Returns:

    """

    default_name = 'default_name'
    try:
        # not allowed to start with XML
        if name.upper().startswith('XML'):
            name = '_{}'.format(name)

        # not allowed to start with something other than letter or underscore
        if not name[0].isalpha() or name[0] == '_':
            name = '_{}'.format(name)

        # not allowed to have spaces
        name = name.replace(" ", "")

        if len(name) == 0:
            name = default_name
    except:
        name = default_name

    return name


def _create_xsd_element(tag, attrib):
    """Create an XSD element.

    Args:
        tag:
        attrib:

    Returns:

    """

    if tag not in ['element', 'include', 'import']:
        raise CoreError('Unable to create XSD element: invalid tag')

    xsd_element = XSDTree.create_element("{0}{1}".format(LXML_SCHEMA_NAMESPACE, tag), attrib=attrib)

    return xsd_element
