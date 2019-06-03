""" Xml utils for the core applications
"""
import json
from collections import OrderedDict
from urlparse import urlparse

import xmltodict
from django.core.urlresolvers import reverse

import core_main_app.commons.exceptions as exceptions
import xml_utils.commons.constants as xml_utils_constants
import xml_utils.xml_validation.validation as xml_validation
from core_main_app.commons.exceptions import XMLError
from core_main_app.settings import XERCES_VALIDATION, SERVER_URI
from core_main_app.utils.resolvers.resolver_utils import lmxl_uri_resolver
from core_main_app.utils.urls import get_template_download_pattern
from xml_utils.commons.constants import XSL_NAMESPACE
from xml_utils.xsd_hash import xsd_hash
from xml_utils.xsd_tree.operations.namespaces import get_namespaces
from xml_utils.xsd_tree.xsd_tree import XSDTree


def validate_xml_schema(xsd_tree):
    """Check if XSD schema is valid, send XSD Schema to server to be validated if XERCES_VALIDATION is true.

    Args:
        xsd_tree:

    Returns: None if no errors, string otherwise

    """
    if XERCES_VALIDATION:
        try:
            error = xml_validation.xerces_validate_xsd(xsd_tree)
        except Exception:
            error = xml_validation.lxml_validate_xsd(xsd_tree, lmxl_uri_resolver())
    else:
        error = xml_validation.lxml_validate_xsd(xsd_tree, lmxl_uri_resolver())

    return error


def validate_xml_data(xsd_tree, xml_tree):
    """Check if XML data is valid, send XML data to server to be validated if XERCES_VALIDATION is true

    Args:
        xsd_tree:
        xml_tree:

    Returns:None if no errors, string otherwise

    """
    if XERCES_VALIDATION:
        try:
            error = xml_validation.xerces_validate_xml(xsd_tree, xml_tree)
        except Exception:
            error = xml_validation.lxml_validate_xml(xsd_tree, xml_tree, lmxl_uri_resolver())
    else:
        error = xml_validation.lxml_validate_xml(xsd_tree, xml_tree, lmxl_uri_resolver())

    return error


def is_schema_valid(xsd_string):
    """Test if the schema is valid to be uploaded.

    Args:
        xsd_string:

    Returns:

    """
    if not is_well_formed_xml(xsd_string):
        raise exceptions.XMLError('Uploaded file is not well formatted XML.')

    # Check schema support by the core
    errors = _check_core_support(xsd_string)
    if len(errors) > 0:
        errors_str = ", ".join(errors)
        raise exceptions.CoreError(errors_str)

    error = validate_xml_schema(XSDTree.build_tree(xsd_string))
    if error is not None:
        raise exceptions.XSDError(error)


def is_well_formed_xml(xml_string):
    """True if well formatted XML.

    Args:
        xml_string:

    Returns:

    """
    # is it a valid XML document?
    try:
        XSDTree.build_tree(xml_string)
    except Exception:
        return False

    return True


def has_xsl_namespace(xml_string):
    """True if XML has the XSL namespace.

    Args:
        xml_string:

    Returns:

    """
    has_namespace = False
    try:
        has_namespace = XSL_NAMESPACE in get_namespaces(xml_string).values()
    except Exception:
        pass

    return has_namespace


def unparse(json_dict):
    """Unparse JSON data.

    Args:
        json_dict:

    Returns:

    """
    json_dump_string = json.dumps(json_dict)
    preprocessed_dict = json.loads(json_dump_string,
                                   parse_float=_parse_numbers,
                                   parse_int=_parse_numbers,
                                   object_pairs_hook=OrderedDict)
    return xmltodict.unparse(preprocessed_dict)


def raw_xml_to_dict(raw_xml, postprocessor=None):
    """Transform a raw xml to dict. Returns an empty dict if the parsing failed.

    Args:
        raw_xml:
        postprocessor:

    Returns:

    """
    try:
        dict_raw = xmltodict.parse(raw_xml, postprocessor=postprocessor)
        return dict_raw
    except xmltodict.expat.ExpatError:
        raise exceptions.XMLError("An unexpected error happened during the XML parsing.")


def remove_lists_from_xml_dict(xml_dict, max_list_size=0):
    """Remove from dictionary the lists that exceed max list size.

    Args:
        xml_dict:
        max_list_size:

    Returns:

    """
    # init list of keys to delete
    keys_to_delete = []
    # iterate key, values
    for key, value in xml_dict.iteritems():
        # if value is a list
        if isinstance(value, list):
            # if list's size is higher than maximum size
            if len(value) > max_list_size:
                # mark key for deletion
                keys_to_delete.append(key)
        # if value is a dict
        elif isinstance(value, dict):
            # continue recursion on value
            remove_lists_from_xml_dict(value, max_list_size)
    # delete keys marked for deletion
    for key_to_delete in keys_to_delete:
        del xml_dict[key_to_delete]


def get_template_with_server_dependencies(xsd_string, dependencies):
    """Return the template with schema locations pointing to the server.

    Args:
        xsd_string:
        dependencies:

    Returns:

    """
    # replace includes/imports by API calls (get dependencies starting by the imports)
    try:
        xsd_tree = update_dependencies(xsd_string, dependencies)
    except Exception, e:
        raise exceptions.XSDError("Something went wrong during dependency update.")

    # validate the schema
    try:
        error = validate_xml_schema(xsd_tree)
    except Exception, e:
        raise exceptions.XSDError("Something went wrong during XSD validation.")

    # is it a valid XML document ?
    if error is None:
        updated_xsd_string = XSDTree.tostring(xsd_tree)
    else:
        raise exceptions.XSDError(error.replace("'", ""))

    return updated_xsd_string


def get_hash(xml_string):
    """Get the hash of an XML string.

    Args:
        xml_string:

    Returns:

    """
    try:
        return xsd_hash.get_hash(xml_string)
    except Exception, e:
        raise exceptions.XSDError("Something wrong happened during the hashing.")


def post_processor(path, key, value):
    """ Called after XML to JSON transformation.

        Parameters:
            path:
            key:
            value:

        Returns:
    """
    return key, convert_value(value)


def convert_value(value):
    """ Convert the value to the true type

    Args:
        value:

    Returns:

    """
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            return value


def get_imports_and_includes(xsd_string):
    """Get a list of imports and includes in the file.

    Args:
        xsd_string:

    Returns: list of imports, list of includes

    """
    xsd_tree = XSDTree.build_tree(xsd_string)
    # get the imports
    imports = xsd_tree.findall("{}import".format(xml_utils_constants.LXML_SCHEMA_NAMESPACE))
    # get the includes
    includes = xsd_tree.findall("{}include".format(xml_utils_constants.LXML_SCHEMA_NAMESPACE))
    return imports, includes


def update_dependencies(xsd_string, dependencies):
    """Update dependencies of the schemas with given dependencies.

    Args:
        xsd_string:
        dependencies:

    Returns:

    """
    # build the tree
    xsd_tree = XSDTree.build_tree(xsd_string)
    # get the imports
    xsd_imports = xsd_tree.findall("{}import".format(xml_utils_constants.LXML_SCHEMA_NAMESPACE))
    # get the includes
    xsd_includes = xsd_tree.findall("{}include".format(xml_utils_constants.LXML_SCHEMA_NAMESPACE))

    for schema_location, dependency_id in dependencies.iteritems():
        if dependency_id is not None:
            for xsd_include in xsd_includes:
                if schema_location == xsd_include.attrib['schemaLocation']:
                    xsd_include.attrib['schemaLocation'] = _get_schema_location_uri(dependency_id)

            for xsd_import in xsd_imports:
                if schema_location == xsd_import.attrib['schemaLocation']:
                    xsd_import.attrib['schemaLocation'] = _get_schema_location_uri(dependency_id)
    return xsd_tree


def get_local_dependencies(xsd_string):
    """Get local dependencies from an xsd.

        Args:
            xsd_string: XSD as string.

        Returns:
            Local dependencies

        """
    # declare list of dependencies
    dependencies = []
    # Get includes and imports
    imports, includes = get_imports_and_includes(xsd_string)
    # list of includes and imports
    xsd_includes_imports = imports + includes

    # get pattern to match the url to download a template
    pattern = get_template_download_pattern()

    for xsd_include_import in xsd_includes_imports:
        if xsd_include_import.attrib['schemaLocation'].startswith(SERVER_URI):
            try:
                # parse dependency url
                url = urlparse(xsd_include_import.attrib['schemaLocation'])
                # get id from url
                object_id = pattern.match(url.path).group('pk')
                # add id to list of internal dependencies
                dependencies.append(object_id)
            except Exception:
                raise XMLError("Local dependency schemaLocation is not well formed.")

    return dependencies


def _check_core_support(xsd_string):
    """Check that the format of the the schema is supported by the current version of the Core.

    Args:
        xsd_string:

    Returns:

    """
    # list of errors
    errors = []

    # build xsd tree
    xsd_tree = XSDTree.build_tree(xsd_string)

    # get the imports
    imports = xsd_tree.findall("{}import".format(xml_utils_constants.LXML_SCHEMA_NAMESPACE))
    # get the includes
    includes = xsd_tree.findall("{}include".format(xml_utils_constants.LXML_SCHEMA_NAMESPACE))

    if len(imports) != 0 or len(includes) != 0:
        for el_import in imports:
            if 'schemaLocation' not in el_import.attrib:
                errors.append("The attribute schemaLocation of import is required but missing.")
            elif ' ' in el_import.attrib['schemaLocation']:
                errors.append("The use of namespace in import elements is not supported.")
        for el_include in includes:
            if 'schemaLocation' not in el_include.attrib:
                errors.append("The attribute schemaLocation of include is required but missing.")
            elif ' ' in el_include.attrib['schemaLocation']:
                errors.append("The use of namespace in include elements is not supported.")

    return errors


def _parse_numbers(num_str):
    """Parse numbers from JSON.

    Returns:
        str: parsed string
    """
    return str(num_str)


def _get_schema_location_uri(schema_id):
    """Get an URI of the schema location on the system from an id.

    Args:
        schema_id:

    Returns:

    """
    url = reverse('core_main_app_rest_template_download', kwargs={'pk': str(schema_id)})
    return str(SERVER_URI) + url


def xsl_transform(xml_string, xslt_string):
    """Apply transformation to xml.

    Args:
        xml_string:
        xslt_string:

    Returns:

    """
    try:
        # Build the XSD and XSLT tree
        xslt_tree = XSDTree.build_tree(xslt_string)
        xsd_tree = XSDTree.build_tree(xml_string)

        # Get the XSLT transformation and transform the XSD
        transform = XSDTree.transform_to_xslt(xslt_tree)
        transformed_tree = transform(xsd_tree)
        return str(transformed_tree)
    except Exception:
        raise exceptions.CoreError("An unexpected exception happened while transforming the XML")

