"""Parser class
"""
import logging
import numbers
import re
import sys
import traceback
from urlparse import parse_qsl

from lxml import etree

from core_main_app.commons.exceptions import CoreError
from core_main_app.utils.requests_utils.requests_utils import send_get_request
from core_main_app.utils.xsd_flattener.xsd_flattener_database_url import XSDFlattenerDatabaseOrURL
from core_parser_app.components.data_structure_element import api as data_structure_element_api
from core_parser_app.components.data_structure_element.models import DataStructureElement
from core_parser_app.components.module import api as module_api
from core_parser_app.settings import MODULE_TAG_NAME
from core_parser_app.tools.parser.exceptions import ParserError
from core_parser_app.tools.parser.renderer.list import ListRenderer
from core_parser_app.tools.parser.utils.rendering import format_tooltip
from core_parser_app.tools.parser.utils.xml import get_app_info_options, \
    get_element_occurrences, get_attribute_occurrences, get_module_url
from xml_utils.commons.constants import LXML_SCHEMA_NAMESPACE
from xml_utils.xsd_tree.operations.appinfo import add_appinfo_child_to_element
from xml_utils.xsd_tree.operations.namespaces import get_namespaces, get_default_prefix, get_target_namespace
from xml_utils.xsd_tree.xsd_tree import XSDTree
from xml_utils.xsd_types.xsd_types import get_xsd_types

logger = logging.getLogger(__name__)


##################################################
# Part I: Utilities
##################################################

def load_schema_data_in_db(xsd_data):
    """
    Load data in database
    :param xsd_data:
    :return:
    """
    xsd_element = DataStructureElement()
    xsd_element.tag = xsd_data['tag']

    if xsd_data['value'] is not None:
        if isinstance(xsd_data['value'], numbers.Number):
            element_value = str(xsd_data['value'])
        else:
            element_value = xsd_data['value']

        element_value = element_value.lstrip()
        xsd_data['value'] = element_value.rstrip()

    xsd_element.value = xsd_data['value']

    if 'options' in xsd_data:
        if xsd_element.tag == 'module' and xsd_data['options']['data'] is not None:
            module_data = xsd_data['options']['data'].encode('utf-8')
            module_data = module_data.lstrip()
            xsd_data['options']['data'] = module_data.rstrip()

        xsd_element.options = xsd_data['options']

    if 'children' in xsd_data:
        children = []

        for child in xsd_data['children']:
            child_db = load_schema_data_in_db(child)
            children.append(child_db)

        if len(children) > 0:
            xsd_element.children = children

    if xsd_element.tag == 'choice-iter':
        if xsd_element.value is None:
            xsd_element.value = str(xsd_element.children[0].pk)
        else:  # Value set => Put the pk of the displayed child
            child_index = int(xsd_element.value)
            xsd_element.value = str(xsd_element.children[child_index].pk)

    data_structure_element_api.upsert(xsd_element)
    return xsd_element


# TODO: look into using delete cascade
# FIXME: not removing all data structure elements
def delete_branch_from_db(element_id):
    """
    Delete a branch from the database
    :param element_id:
    :return:
    """
    element = data_structure_element_api.get_by_id(element_id)

    for child in element.children:
        delete_branch_from_db(str(child.pk))

    element.delete()


def update_branch_xpath(element):
    """
    Update the xpath in a branch
    :param element:
    :return:
    """
    element_xpath = element.options['xpath']['xml']
    xpath_index = 1

    for child in element.children:
        update_root_xpath(child, element_xpath, xpath_index)
        xpath_index += 1


# TODO: needs to be reworked
def remove_child_element(data_structure_element, to_remove):
    """Removes a child element and its branch from db

    Args:
        data_structure_element:
        to_remove:

    Returns:

    """
    # remove child from element
    data_structure_element_api.pull_children(data_structure_element, to_remove)
    # update children xpaths
    update_branch_xpath(data_structure_element)

    # Deleting the branch from the database
    delete_branch_from_db(str(to_remove.id))

    # TODO: Sequence elem might not work
    if len(data_structure_element.children) == 0:
        elem_iter = DataStructureElement()

        if data_structure_element.tag == 'element':
            elem_iter.tag = 'elem-iter'
        elif data_structure_element.tag == 'choice':
            elem_iter.tag = 'choice-iter'
        elif data_structure_element.tag == 'sequence':
            elem_iter.tag = 'sequence-iter'

        data_structure_element_api.upsert(elem_iter)
        data_structure_element_api.add_to_set(data_structure_element, [elem_iter])

    return data_structure_element


def update_root_xpath(element, xpath, index):
    """
    Update the Xpath of the root
    :param element:
    :param xpath:
    :param index:
    :return:
    """
    element_options = element.options

    if 'xpath' in element_options:
        xml_xpath = element_options['xpath']['xml']
        element_options['xpath']['xml'] = xml_xpath.replace(xpath + '[1]', xpath + '[' + str(index) + ']', 1)

        element.update(set__options=element_options)
        element.reload()

    for child in element.children:
        update_root_xpath(child, xpath, index)


def get_nodes_xpath(elements, xml_tree, download_enabled=True):
    """Perform a lookup in subelements to build xpath.

    Get nodes' xpath, only one level deep. It's not going to every leaves. Only need to know if the
    node is here.

    Parameters:
        elements: XML element
        xml_tree: xml_tree
        download_enabled:
    """
    # FIXME Making one function with get_subnode_xpath should be possible, both are doing the same job
    # FIXME same problems as in get_subnodes_xpath
    xpaths = []
    element_tag = None
    schema_location = None

    for element in elements:
        if element.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
            if 'name' in element.attrib:
                xpaths.append({'name': element.attrib['name'], 'element': element})
            elif 'ref' in element.attrib:
                # check if XML element or attribute
                if element.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
                    element_tag = 'element'
                elif element.tag == "{0}attribute".format(LXML_SCHEMA_NAMESPACE):
                    element_tag = 'attribute'

                # get schema namespaces
                xml_tree_str = XSDTree.tostring(xml_tree)
                namespaces = get_namespaces(xml_tree_str)
                ref = element.attrib['ref']
                ref_element, ref_tree, schema_location = get_ref_element(xml_tree, ref, namespaces,
                                                                         element_tag, schema_location,
                                                                         download_enabled=download_enabled)

                if ref_element is not None:
                    xpaths.append({'name': ref_element.attrib.get('name'), 'element': ref_element})
        else:
            xpaths.extend(get_nodes_xpath(element, xml_tree, download_enabled=download_enabled))
    return xpaths


def lookup_occurs(element, xml_tree, full_path, edit_data_tree, download_enabled=True):
    """Do a lookup in data to get the number of occurrences of a sequence or choice without a name (not within a named
    complextype).

    get the number of times the sequence appears in the XML document that we are loading for editing
    algorithm:
    get all the possible nodes that can appear in the sequence
    for each node, count how many times it's found in the data
    the maximum count is the number of occurrences of the sequence
    only works if data are determinist enough: means we don't have an element outside the sequence, and the same in
    the sequence

    Parameters:
        element: XML element
        xml_tree: XML schema tree
        full_path: current node XPath
        edit_data_tree: XML data tree
    """
    # FIXME this function is not returning the correct output
    # get all possible xpaths of sub nodes
    xpaths = get_nodes_xpath(element, xml_tree, download_enabled=download_enabled)
    elements_found = []

    # get target namespace prefix if one declared
    xml_tree_str = XSDTree.tostring(xml_tree)
    namespaces = get_namespaces(xml_tree_str)
    target_namespace, target_namespace_prefix = get_target_namespace(xml_tree, namespaces)

    # check if xpaths find a match in the document
    for xpath in xpaths:
        edit_elements = edit_data_tree.xpath(full_path + '/' + target_namespace_prefix + xpath['name'],
                                             namespaces=namespaces)
        element_path = get_xml_xpath(xml_tree, full_path, "element", xpath['name'], target_namespace,
                                     target_namespace_prefix)
        edit_elements = edit_data_tree.xpath(element_path, namespaces=namespaces)
        elements_found.extend(edit_elements)

    return elements_found


def is_module_multiple(element):
    """ Checks if the module is multiple (means it manages the occurrences)

    :param element:
    :return:
    """
    module_url = get_module_url(element)
    if module_url is not None:
        module = module_api.get_by_url(module_url.path)
        return module.multiple

    return False


def get_xml_element_data(xsd_element, xml_element):
    """
    Return the content of an xml element
    :param xsd_element:
    :param xml_element:
    :return:
    """

    reload_data = None
    prefix = '{0}'.format(LXML_SCHEMA_NAMESPACE)

    # get data
    if xsd_element.tag == prefix + "element":
        # leaf: get the value
        if len(list(xml_element)) == 0:
            if hasattr(xml_element, 'text') and xml_element.text is not None:
                reload_data = xml_element.text
            else:  # if xml_element.text is None
                reload_data = ''
        else:  # branch: get the whole branch
            reload_data = XSDTree.tostring(xml_element)
    elif xsd_element.tag == prefix + "attribute":
        return str(xml_element)
    elif xsd_element.tag == prefix + "complexType" or xsd_element.tag == prefix + "simpleType":
        # leaf: get the value
        if len(list(xml_element)) == 0:
            if hasattr(xml_element, 'text') and xml_element.text is not None:
                reload_data = xml_element.text
            else:  # xml_element.text is None
                reload_data = ''
        else:  # branch: return children
            try:
                if list(xml_element) > 0:
                    reload_data = ''
                    for child in list(xml_element):
                        reload_data += XSDTree.tostring(child)
            except:
                # FIXME in which case would we need that?
                reload_data = str(xml_element)

    return reload_data


def get_element_type(element, xml_tree, namespaces, default_prefix, target_namespace_prefix, schema_location=None,
                     attr='type', download_enabled=True):
    """ Get XSD type to render. Returns the tree where the type was found.

    Parameters:
        element: XML element
        xml_tree: XSD tree of the template
        namespaces:
        default_prefix:
        target_namespace_prefix:
        schema_location:
        attr:
        download_enabled

    Returns the type if found
        - complexType
        - simpleType

    Returns None otherwise:
        - type from default namespace (xsd:...)
        - no type

    Returns:
        - tree where the type has been found
        - schema location where the type has been found
    """

    element_type = None
    try:
        if attr not in element.attrib:  # element with type declared below it
            for i in range(len(list(element))):
                if element[i].tag == "{0}simpleType".format(LXML_SCHEMA_NAMESPACE) or \
                        element[i].tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):
                    element_type = element[i]
                    break
        else:  # element with type attribute
            if element.attrib.get(attr) in get_xsd_types(default_prefix):
                element_type = element.attrib.get(attr)
                # if default prefix in type name
                if element_type.startswith(default_prefix) and default_prefix != "":
                    # remove default prefix and ':'
                    element_type = element_type[len(default_prefix)+1:]
            elif element.attrib.get(attr) is not None:  # FIXME is it possible?
                # TODO: manage namespaces
                # test if type of the element is a simpleType
                type_name = element.attrib.get(attr)
                if ':' in type_name:
                    type_ns_prefix = type_name.split(":")[0]
                    type_name = type_name.split(":")[1]
                    if type_ns_prefix != target_namespace_prefix:
                        # TODO: manage ref to imported elements (different target namespace)
                        # get all import elements
                        imports = xml_tree.findall('//{}import'.format(LXML_SCHEMA_NAMESPACE))
                        # find the referred document using the prefix
                        # the namespace is declared inline
                        if type_ns_prefix in element.nsmap:
                            for el_import in imports:
                                import_ns = el_import.attrib['namespace']
                                if element.nsmap[type_ns_prefix] == import_ns:
                                    xml_tree, schema_location = import_xml_tree(el_import, download_enabled)
                                    break
                        else:
                            if type_ns_prefix in namespaces:
                                for el_import in imports:
                                    import_ns = el_import.attrib['namespace']
                                    if namespaces[type_ns_prefix] == import_ns:
                                        xml_tree, schema_location = import_xml_tree(el_import, download_enabled)
                                        break

                xpath = "./{0}complexType[@name='{1}']".format(LXML_SCHEMA_NAMESPACE, type_name)
                element_type = xml_tree.find(xpath)
                if element_type is None:
                    # test if type of the element is a simpleType
                    xpath = "./{0}simpleType[@name='{1}']".format(LXML_SCHEMA_NAMESPACE, type_name)
                    element_type = xml_tree.find(xpath)
    except Exception as e:
        exception_message = "Something went wrong in get_element_type:  " + str(e)
        logger.fatal(exception_message)

        element_type = None

    return element_type, xml_tree, schema_location


def import_xml_tree(el_import, download_enabled=True):
    """
    Return tree after downloading import's schemaLocation
    :param el_import:
    :param download_enabled:
    :return:
    """
    # get the location of the schema
    ref_xml_schema_url = el_import.attrib['schemaLocation']
    schema_location = ref_xml_schema_url
    # download the file
    if download_enabled:
        ref_xml_schema_file = send_get_request(ref_xml_schema_url)
        # read the content of the file
        ref_xml_schema_content = ref_xml_schema_file.content
        # build the tree
        xml_tree = XSDTree.build_tree(ref_xml_schema_content)
        # look for includes
        includes = xml_tree.findall('//{}include'.format(LXML_SCHEMA_NAMESPACE))
        # if includes are present
        if len(includes) > 0:
            # create a flattener with the file content
            flattener = XSDFlattenerDatabaseOrURL(ref_xml_schema_content, download_enabled)
            # flatten the includes
            ref_xml_schema_content = flattener.get_flat()
            # build the tree
            xml_tree = XSDTree.build_tree(ref_xml_schema_content)
        return xml_tree, schema_location
    else:
        raise ParserError('Dependency could not be downloaded')


def get_ref_element(xml_tree, ref, namespaces, element_tag, schema_location=None, download_enabled=True):
    """

    Parameters:
        xml_tree:
        ref:
        namespaces:
        element_tag:
        schema_location:
        download_enabled:

    Returns
        - ref_element: ref element when found
        - xml_tree: xml tree where element was found
        - schema_location: location of the schema where the element was found
    """
    if ':' in ref:
        # split the ref element
        ref_split = ref.split(":")
        # get the namespace prefix
        ref_namespace_prefix = ref_split[0]
        # get the element name
        ref_name = ref_split[1]
        # test if referencing element within the same schema (same target namespace)
        target_namespace, target_namespace_prefix = get_target_namespace(xml_tree, namespaces)
        # ref is in the same file
        if target_namespace_prefix == ref_namespace_prefix:
            ref_element = xml_tree.find("./{0}{1}[@name='{2}']".format(LXML_SCHEMA_NAMESPACE,
                                                                       element_tag, ref_name))
        else:  # the ref might be in one of the imports
            # get all import elements
            imports = xml_tree.findall('//{}import'.format(LXML_SCHEMA_NAMESPACE))
            # find the referred document using the prefix
            for el_import in imports:
                import_ns = el_import.attrib['namespace']
                if namespaces[ref_namespace_prefix] == import_ns:
                    xml_tree, schema_location = import_xml_tree(el_import, download_enabled)

                    ref_element = xml_tree.find("./{0}{1}[@name='{2}']".format(LXML_SCHEMA_NAMESPACE,
                                                                               element_tag, ref_name))
                    break
    else:
        ref_element = xml_tree.find("./{0}{1}[@name='{2}']".format(LXML_SCHEMA_NAMESPACE, element_tag, ref))

    return ref_element, xml_tree, schema_location


def get_element_form_default(xsd_tree):
    """
    Get value of ElementFormDefault
    :param xsd_tree:
    :return:
    """

    # default value
    element_form_default = "unqualified"

    root = xsd_tree.getroot()
    if 'elementFormDefault' in root.attrib:
        element_form_default = root.attrib['elementFormDefault']

    return element_form_default


def get_attribute_form_default(xsd_tree):
    """
    Get the value of the attributeFormDefault attribute
    :param xsd_tree:
    :return:
    """
    # default value
    attribute_form_default = "unqualified"

    root = xsd_tree.getroot()
    if 'attributeFormDefault' in root.attrib:
        attribute_form_default = root.attrib['attributeFormDefault']

    return attribute_form_default


def get_element_namespace(element, xsd_tree):
    """
    Get the namespace of the element
    :param element:
    :param xsd_tree:

    :return:
    """
    # get the root of the XSD document
    xsd_root = xsd_tree.getroot()

    # None by default, None means no namespace information needed, different from empty namespace
    element_ns = None

    # check if the element is root
    is_root = False
    # get XSD xpath
    xsd_path = xsd_tree.getpath(element)
    # the element is global (/xs:schema/xs:element)
    if xsd_path.count('/') == 2:
        is_root = True

    # root is always qualified, root from other schemas too
    if is_root:
        # if in a targetNamespace
        if 'targetNamespace' in xsd_root.attrib:
            # get the target namespace
            target_namespace = xsd_root.attrib['targetNamespace']
            element_ns = target_namespace
    else:
        # qualified elements
        if 'elementFormDefault' in xsd_root.attrib and xsd_root.attrib['elementFormDefault'] == 'qualified' \
                or 'attributeFormDefault' in xsd_root.attrib and xsd_root.attrib['attributeFormDefault'] == 'qualified':
            if 'targetNamespace' in xsd_root.attrib:
                # get the target namespace
                target_namespace = xsd_root.attrib['targetNamespace']
                element_ns = target_namespace
        # unqualified elements
        else:
            if 'targetNamespace' in xsd_root.attrib:
                element_ns = ""

    return element_ns


def get_extensions(xml_doc_tree, base_type_name):
    """
    Get all XML extensions of the XML Schema
    :param xml_doc_tree:
    :param base_type_name:
    :return:
    """
    # TODO: look for extensions in imported documents
    # get all extensions of the document
    extensions = xml_doc_tree.findall(".//{0}extension".format(LXML_SCHEMA_NAMESPACE))
    # keep only simple/complex type extensions, no built-in types
    custom_type_extensions = []
    for extension in extensions:
        base = extension.attrib['base']
        # TODO: manage namespaces
        if ":" in base:
            base = base.split(':')[1]
        if base_type_name == base:
            # get parent type that contains the extension
            type_extension = extension.getparent()
            while 'simpleType' not in type_extension.tag and 'complexType' not in type_extension.tag:
                type_extension = type_extension.getparent()
            custom_type_extensions.append(type_extension)

    return custom_type_extensions


def get_xml_xpath(xml_tree, xml_xpath, element_tag, element_name, target_namespace=None, target_namespace_prefix=None,
                  is_ref=False):
    """Returns the xpath of an element

    Args:
        xml_tree:
        xml_xpath:
        element_tag:
        element_name:
        target_namespace:
        target_namespace_prefix:
        is_ref:

    Returns:

    """
    # XML xpath:/root/element
    if element_tag == 'element':
        if target_namespace is not None:
            if target_namespace_prefix != '':
                if get_element_form_default(xml_tree) == "qualified":
                    xml_xpath += '/{0}:{1}'.format(target_namespace_prefix, element_name)
                elif is_ref:
                    xml_xpath += '/{0}:{1}'.format(target_namespace_prefix, element_name)
                elif "{0}:".format(target_namespace_prefix) in xml_xpath:
                    xml_xpath += '/{0}'.format(element_name)
                else:
                    xml_xpath += '/{0}:{1}'.format(target_namespace_prefix, element_name)
            else:
                xml_xpath += '/*[local-name()="{0}"]'.format(element_name)
        else:
            xml_xpath += "/{0}".format(element_name)
    elif element_tag == 'attribute':
        if target_namespace is not None:
            if target_namespace_prefix != '':
                if get_attribute_form_default(xml_tree) == "qualified":
                    xml_xpath += '/@{0}:{1}'.format(target_namespace_prefix, element_name)
                elif is_ref:
                    xml_xpath += '/@{0}:{1}'.format(target_namespace_prefix, element_name)
                elif "{0}:".format(target_namespace_prefix) in xml_xpath:
                    xml_xpath += '/@{0}'.format(element_name)
                else:
                    xml_xpath += '/@{0}:{1}'.format(target_namespace_prefix, element_name)
            else:
                xml_xpath += '/@*[local-name()="{0}"]'.format(element_name)
        else:
            xml_xpath += "/@{0}".format(element_name)

    return xml_xpath


##################################################
# Part II: Schema parsing
##################################################
class XSDParser(object):

    def __init__(self, min_tree=True, ignore_modules=False, collapse=True, auto_key_keyref=True,
                 implicit_extension_base=False, download_dependencies=True, store_type=False):
        """ Initialize XSD Parser

        Args:
            min_tree:
            ignore_modules:
            collapse:
            auto_key_keyref:
            implicit_extension_base:
            download_dependencies:
            store_type:
        """
        self.min_tree = min_tree
        self.ignore_modules = ignore_modules
        self.collapse = collapse
        self.auto_key_keyref = auto_key_keyref
        self.implicit_extension_base = implicit_extension_base
        self.download_dependencies = download_dependencies
        self.store_type = store_type

        self.editing = False
        self.keys = {}
        self.keyrefs = {}

    def generate_form(self, xsd_doc_data, xml_doc_data=None):
        """ Generate form data structure form XML Schema

        Args:
            xsd_doc_data:
            xml_doc_data:

        Returns:

        """

        # flatten the includes
        flattener = XSDFlattenerDatabaseOrURL(xsd_doc_data, self.download_dependencies)
        xml_doc_tree_str = flattener.get_flat()
        xml_doc_tree = XSDTree.build_tree(xml_doc_tree_str)

        # if editing, get the XML data to fill the form
        edit_data_tree = None
        # build the tree from data
        # transform unicode to str to support XML declaration
        if xml_doc_data is not None:
            # Load a parser able to clean the XML from blanks, comments and processing instructions
            clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
            # set the parser
            etree.set_default_parser(parser=clean_parser)
            # xml data not empty
            if xml_doc_data != "":
                # TODO: check from curate that editing works
                self.editing = True
                # load the XML tree from the text
                edit_data_tree = XSDTree.transform_to_xml(xml_doc_data)
            else:
                self.editing = False
        else:  # no data found, not editing
            self.editing = False

        # find all root elements
        elements = xml_doc_tree.findall("./{0}element".format(LXML_SCHEMA_NAMESPACE))

        try:
            form_content = ""
            if len(elements) == 1:  # One root
                form_content = self.generate_element(elements[0],
                                                     xml_doc_tree,
                                                     edit_data_tree=edit_data_tree)
            elif len(elements) > 1:  # Several root
                # look if a default choice to render is defined
                default_choice = False
                for element in elements:
                    app_info = get_app_info_options(element)
                    if 'default' in app_info:
                        form_content = self.generate_element(element,
                                                             xml_doc_tree,
                                                             edit_data_tree=edit_data_tree)
                        default_choice = True
                        break
                if not default_choice:
                    form_content = self.generate_choice(elements,
                                                        xml_doc_tree,
                                                        edit_data_tree=edit_data_tree)
            else:  # len(elements) == 0 (no root element)
                # fixed always false because fixed cannot be on the type
                # TODO: does it make sense to get all simple types too?
                complex_types = xml_doc_tree.findall("./{0}complexType".format(LXML_SCHEMA_NAMESPACE))
                if len(complex_types) > 0:
                    # look if a default choice to render is defined
                    default_choice = False
                    for complex_type in complex_types:
                        app_info = get_app_info_options(complex_type)
                        if 'default' in app_info:
                            form_content = self.generate_choice_extensions([complex_type],
                                                                           xml_doc_tree,
                                                                           edit_data_tree=edit_data_tree)
                            default_choice = True
                            break
                    if not default_choice:
                        form_content = self.generate_choice_extensions(complex_types,
                                                                       xml_doc_tree,
                                                                       edit_data_tree=edit_data_tree)
                else:  # len(complex_types) == 0
                    simple_types = xml_doc_tree.findall("./{0}simpleType".format(LXML_SCHEMA_NAMESPACE))
                    if len(simple_types) == 1:  # 1 simple type found
                        form_content = self.generate_simple_type(simple_types[0],
                                                                 xml_doc_tree,
                                                                 full_path="",
                                                                 edit_data_tree=edit_data_tree)
                    else:
                        raise Exception("No possible root element detected")

            root_element = load_schema_data_in_db(form_content)

            if self.auto_key_keyref:
                root_element.options['keys'] = self.keys
                root_element.options['keyrefs'] = self.keyrefs
                data_structure_element_api.upsert(root_element)

            self.editing = False
            return root_element.pk
        except Exception as e:
            exc_info = sys.exc_info()

            # Adding information to the Exception message
            exception_message = "Schema parsing failed: " + str(e)
            logger.fatal(exception_message)

            traceback.print_exception(*exc_info)
            del exc_info

            self.editing = False
            raise Exception(exception_message)

    def generate_element(self, element, xml_tree, choice_counter=None, full_path="", edit_data_tree=None,
                         schema_location=None, xml_element=None, force_generation=False):
        """ Generate data structure for an XML element

        Args:
            element:
            xml_tree:
            choice_counter:
            full_path:
            edit_data_tree:
            schema_location:
            xml_element:
            force_generation:

        Returns:

        """
        # FIXME if elif without else need to be corrected
        # FIXME Support for unique is not present
        # FIXME Support for key / keyref
        app_info = get_app_info_options(element)

        # check if the element has a module
        _has_module = False
        _is_multiple = False
        if not self.ignore_modules:
            module_url = get_module_url(element)
            _has_module = True if module_url is not None else False
            # check if the module manages the occurrences by itself
            _is_multiple = is_module_multiple(element) if _has_module else False

        # FIXME see if we can avoid these basic initialization
        # FIXME this is not necessarily true (see attributes)
        min_occurs = 1
        max_occurs = 1

        text_capitalized = ''
        element_tag = ''
        edit_elements = []
        ##############################################

        # check if XML element or attribute
        if element.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
            min_occurs, max_occurs = get_element_occurrences(element)
            element_tag = 'element'
        elif element.tag == "{0}attribute".format(LXML_SCHEMA_NAMESPACE):
            min_occurs, max_occurs = get_attribute_occurrences(element)
            element_tag = 'attribute'

        # get schema namespaces
        xml_tree_str = XSDTree.tostring(xml_tree)
        namespaces = get_namespaces(xml_tree_str)

        db_element = {
            'tag': element_tag,  # 'element' or 'attribute'
            'options': {
                'name': text_capitalized,
                'min': min_occurs,
                'max': max_occurs,
                'module': None if not _has_module else True,
                'xpath': {
                    'xsd': None,
                    'xml': full_path
                },
                'schema_location': schema_location,
            },
            'value': None,
            'children': []
        }

        is_ref = False
        # get the name of the element, go find the reference if there's one
        if 'ref' in element.attrib:  # type is a reference included in the document
            is_ref = True
            ref = element.attrib['ref']
            download_enabled = self.download_dependencies
            ref_element, xml_tree, schema_location = get_ref_element(xml_tree, ref, namespaces,
                                                                     element_tag, schema_location,
                                                                     download_enabled=download_enabled)
            if ref_element is not None:
                text_capitalized = ref_element.attrib.get('name')
                element = ref_element
                # check if the element has a module
                _has_module = False
                if not self.ignore_modules:
                    module_url = get_module_url(element)
                    _has_module = True if module_url is not None else False
            else:
                # the element was not found where it was supposed to be
                # could be a use case too complex for the current parser
                warning_message = "Ref element not found: " + str(element.attrib)
                logger.warning(warning_message)

                return db_element
        else:
            text_capitalized = element.attrib.get('name')

        xml_tree_str = XSDTree.tostring(xml_tree)
        namespaces = get_namespaces(xml_tree_str)
        target_namespace, target_namespace_prefix = get_target_namespace(xml_tree, namespaces)

        full_path = get_xml_xpath(xml_tree, full_path, element_tag, text_capitalized, target_namespace,
                                  target_namespace_prefix, is_ref)

        # print full_path

        # XSD xpath: /element/complexType/sequence
        xsd_xpath = xml_tree.getpath(element)

        db_element['options']['name'] = element.attrib.get('name')
        db_element['options']['xpath']['xsd'] = xsd_xpath
        db_element['options']['xpath']['xml'] = full_path
        if self.store_type:
            db_element['options']['type'] = element.attrib['type'] if 'type' in element.attrib else None

        # init variables for buttons management
        nb_occurrences = 1  # nb of occurrences to render (can't be 0 or the user won't see this element at all)
        nb_occurrences_data = min_occurs  # nb of occurrences in loaded data or in form being rendered (can be 0)
        use = ""
        removed = False

        # loading data in the form
        if self.editing:
            if xml_element is None:
                # get the number of occurrences in the data
                edit_elements = edit_data_tree.xpath(full_path, namespaces=namespaces)
                nb_occurrences_data = len(edit_elements)
            else:
                if xml_element is False:  # explicitly say to not generate the element
                    edit_elements = []
                    nb_occurrences_data = 1
                else:
                    edit_elements = [xml_element]
                    nb_occurrences_data = 1

            if nb_occurrences_data == 0:
                use = "removed"
                removed = True

        else:  # starting an empty form
            # Don't generate the element if not necessary
            if self.min_tree and min_occurs == 0:
                use = "removed"
                removed = True

        if _has_module and _is_multiple:
            # block maxOccurs to one, the module should take care of occurrences when the element is replaced
            nb_occurrences = 1
            # max_occurs = 1
        elif nb_occurrences_data > nb_occurrences:
            nb_occurrences = nb_occurrences_data

        # get the element namespace
        element_ns = get_element_namespace(element, xml_tree)
        # set the element namespace
        # tag_ns = ' xmlns="{0}" '.format(element_ns) if element_ns is not None else ''
        ns_prefix = None
        if element_tag == "attribute" and target_namespace is not None:
            for prefix, ns in namespaces.iteritems():
                if ns == target_namespace:
                    ns_prefix = prefix
                    break

        # get the element type
        default_prefix = get_default_prefix(namespaces)

        db_element['options']['schema_location'] = schema_location
        db_element['options']['xmlns'] = element_ns
        db_element['options']['ns_prefix'] = ns_prefix

        download_enabled = self.download_dependencies
        element_type, xml_tree, schema_location = get_element_type(element, xml_tree, namespaces,
                                                                   default_prefix, target_namespace_prefix,
                                                                   schema_location, download_enabled=download_enabled)

        # management of elements inside a choice (don't display if not part of the currently selected choice)
        if choice_counter is not None:
            if self.editing:
                if len(edit_elements) == 0:
                    if self.min_tree:
                        return db_element
            else:
                if choice_counter > 0:
                    if self.min_tree:
                        return db_element

        if force_generation:
            nb_occurrences = 1
            removed = False

        if not self.ignore_modules:
            # if auto key/keyref is True, go find keys/keyrefs in element scope
            if self.auto_key_keyref:
                # TODO: for now, support key/keyref for attributes only
                if element_tag == 'attribute':
                    if self.is_key(element, full_path):
                        _has_module = True
                        db_element['options']['module'] = _has_module
                    elif self.is_keyref(element, full_path):
                        _has_module = True
                        db_element['options']['module'] = _has_module
                elif element_tag == 'element':
                    # look if key/keyrefs are defined for the scope of this element
                    self.manage_key_keyref(element, full_path)

        for x in range(0, int(nb_occurrences)):
            db_elem_iter = {
                'tag': 'elem-iter',
                'value': None,
                'children': []
            }

            # get the use from app info element
            app_info_use = app_info['use'] if 'use' in app_info else ''
            app_info_use = app_info_use if app_info_use is not None else ''
            use += ' ' + app_info_use

            label = app_info['label'] if 'label' in app_info else text_capitalized
            label = label if label is not None else ''

            db_element['options']['label'] = label

            # if element not removed
            if not removed:
                # if module is present, replace default input by module
                if _has_module:
                    xml_path = full_path
                    if not _is_multiple:
                        xml_path = '{0}[{1}]'.format(full_path, str(x + 1))

                    module = self.generate_module(element, xsd_xpath, xml_path, xml_tree=xml_tree,
                                                  edit_data_tree=edit_data_tree)

                    db_elem_iter['children'].append(module)
                else:  # generate the type
                    # get the default value (from xsd or from loaded xml)
                    default_value = ""
                    if self.editing:
                        # if elements are found at this xpath
                        if len(edit_elements) > 0:
                            # it is an XML element
                            if element_tag == 'element':
                                # get the value of the element x
                                if edit_elements[x].text is not None:
                                    # set the value of the element
                                    default_value = edit_elements[x].text
                            # it is an XMl attribute
                            elif element_tag == 'attribute':
                                # get the value of the attribute
                                if edit_elements[x] is not None:
                                    # set the value of the element
                                    if isinstance(edit_elements[x], numbers.Number):
                                        default_value = str(edit_elements[x])
                                    else:
                                        default_value = edit_elements[x]
                    elif 'default' in element.attrib:
                        # if the default attribute is present
                        default_value = element.attrib['default']

                    if 'fixed' in element.attrib:
                        # if the fixed attribute is present
                        is_fixed = True
                        default_value = element.attrib['fixed']
                    else:
                        is_fixed = False

                    default_value = default_value.strip()

                    if not isinstance(element_type, etree._Element):  # no complex/simple type
                        placeholder = app_info['placeholder'] if 'placeholder' in app_info else ''
                        tooltip = format_tooltip(app_info['tooltip']) if 'tooltip' in app_info else ''
                        use = app_info['use'] if 'use' in app_info else ''

                        db_child = {
                            'tag': 'input',
                            'options': {
                                'placeholder': placeholder,
                                'tooltip': tooltip,
                                'use': use,
                                'input_type': element_type
                            },
                            'value': default_value
                        }
                    else:  # complex/simple type

                        if element_type.tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):
                            complex_type_result = self.generate_complex_type(element_type, xml_tree,
                                                                             full_path=full_path + '[' + str(
                                                                                 x + 1) + ']',
                                                                             edit_data_tree=edit_data_tree,
                                                                             default_value=default_value,
                                                                             is_fixed=is_fixed,
                                                                             schema_location=schema_location)
                            db_child = complex_type_result
                        elif element_type.tag == "{0}simpleType".format(LXML_SCHEMA_NAMESPACE):
                            simple_type_result = self.generate_simple_type(element_type, xml_tree,
                                                                           full_path=full_path + '[' + str(x + 1) + ']',
                                                                           edit_data_tree=edit_data_tree,
                                                                           default_value=default_value,
                                                                           is_fixed=is_fixed,
                                                                           schema_location=schema_location)
                            db_child = simple_type_result

                    db_child['options']['fixed'] = is_fixed
                    db_elem_iter['children'].append(db_child)

            db_element['children'].append(db_elem_iter)

        return db_element

    def generate_element_absent(self, request, element_id, xsd_doc_data, renderer_class=ListRenderer):
        """ Generate data structure for an XML element absent from the tree

        Args:
            request:
            element_id:
            xsd_doc_data:
            renderer_class:

        Returns:

        """

        sub_element = data_structure_element_api.get_by_id(element_id)
        element_list = data_structure_element_api.get_all_by_child_id(element_id)

        if self.auto_key_keyref:
            self.init_key_keyref(sub_element)

        if len(element_list) == 0:
            raise ValueError("No SchemaElement found")
        elif len(element_list) > 1:
            raise ValueError("More than one SchemaElement found")

        schema_element = element_list[0]

        schema_location = None
        if 'schema_location' in schema_element.options:
            schema_location = schema_element.options['schema_location']

        # if the xml element is from an imported schema
        if schema_location is not None:
            # open the imported file
            download_enabled = self.download_dependencies
            if download_enabled:
                ref_xml_schema_file = send_get_request(schema_element.options['schema_location'])
                # get the content of the file
                ref_xml_schema_content = ref_xml_schema_file.content
                # build the XML tree
                xml_doc_tree = XSDTree.build_tree(ref_xml_schema_content)
                # get the namespaces from the imported schema
                namespaces = get_namespaces(ref_xml_schema_content)
            else:
                raise ParserError('Dependency could not be downloaded')
        else:
            # build the XML tree
            xml_doc_tree = XSDTree.build_tree(xsd_doc_data)
            # get the namespaces
            namespaces = get_namespaces(xsd_doc_data)

        # flatten the includes
        download_enabled = self.download_dependencies
        flattener = XSDFlattenerDatabaseOrURL(XSDTree.tostring(xml_doc_tree), download_enabled)
        xml_doc_tree_str = flattener.get_flat()
        xml_doc_tree = XSDTree.build_tree(xml_doc_tree_str)

        xpath_element = schema_element.options['xpath']
        xsd_xpath = xpath_element['xsd']

        xml_xpath = None
        if 'xml' in xpath_element:
            xml_xpath = xpath_element['xml']

        xml_element = xml_doc_tree.xpath(xsd_xpath, namespaces=namespaces)[0]

        if 'min' in schema_element.options:
            xml_element.attrib['minOccurs'] = str(schema_element.options['min'])

        if 'max' in schema_element.options:
            if schema_element.options['max'] != -1:
                xml_element.attrib['maxOccurs'] = str(schema_element.options['max'])
            else:
                xml_element.attrib['maxOccurs'] = "unbounded"

        # generating a choice, generate the parent element
        if schema_element.tag == "choice":
            # can use generate_element to generate a choice never generated
            db_tree = self.generate_choice(xml_element, xml_doc_tree,
                                           full_path=xml_xpath,
                                           force_generation=True)
        elif schema_element.tag == 'sequence':
            db_tree = self.generate_sequence(xml_element, xml_doc_tree,
                                             full_path=xml_xpath,
                                             force_generation=True)
        else:
            # can't directly use generate_element because only need the body of the element not its title
            # provide xpath without element name because already generated in generate_element
            db_tree = self.generate_element(xml_element, xml_doc_tree, full_path=xml_xpath.rsplit('/', 1)[0],
                                            force_generation=True)

        # Saving the tree in MongoDB
        tree_root = load_schema_data_in_db(db_tree)
        generated_element = tree_root.children[0]

        # Updating the schema element
        children = schema_element.children
        element_index = children.index(sub_element)

        children.insert(element_index + 1, generated_element)
        schema_element.update(set__children=children)

        if len(sub_element.children) == 0:
            schema_element_to_pull = data_structure_element_api.get_by_id(element_id)
            schema_element.update(pull__children=schema_element_to_pull)

        schema_element.reload()
        update_branch_xpath(schema_element)

        tree_root_options = tree_root.options
        tree_root_options['real_root'] = str(schema_element.pk)

        tree_root.update(set__options=tree_root_options)
        tree_root.reload()

        renderer = renderer_class(tree_root, request)
        html_form = renderer.render(True)

        tree_root.delete()
        return html_form

    def generate_sequence(self, element, xml_tree, choice_counter=None, full_path="", edit_data_tree=None,
                          schema_location=None, force_generation=False):
        """ Generate data structure for an XML sequence

        Args:
            element:
            xml_tree:
            choice_counter:
            full_path:
            edit_data_tree:
            schema_location:
            force_generation:

        Returns:

        """
        # (annotation?,(element|group|choice|sequence|any)*)
        # FIXME implement group, any

        min_occurs, max_occurs = get_element_occurrences(element)

        # XSD xpath
        xsd_xpath = xml_tree.getpath(element)

        db_element = {
            'tag': 'sequence',
            'options': {
                'min': min_occurs,
                'max': max_occurs,
                'xpath': {
                    'xsd': xsd_xpath,
                    'xml': full_path
                },
                'schema_location': schema_location
            },
            'value': None,
            'children': []
        }

        if min_occurs != 1 or max_occurs != 1:
            # init variables for buttons management
            nb_occurrences = 1  # nb of occurrences to render (can't be 0 or the user won't see this element at all)
            nb_occurrences_data = min_occurs  # nb of occurrences in loaded data or in form being rendered (can be 0)

            # loading data in the form
            if self.editing:
                # get the number of occurrences in the data
                download_enabled = self.download_dependencies
                elements_found = lookup_occurs(element, xml_tree, full_path, edit_data_tree,
                                               download_enabled=download_enabled)
                if max_occurs != 1:
                    nb_occurrences_data = len(elements_found)
                else:
                    if len(elements_found) > 0:
                        nb_occurrences_data = 1

            if nb_occurrences_data > nb_occurrences:
                nb_occurrences = nb_occurrences_data

            # keeps track of elements to display depending on the selected choice
            if choice_counter is not None:
                if self.editing:
                    if nb_occurrences == 0:
                        if self.min_tree:
                            return db_element
                else:
                    if choice_counter > 0:
                        if self.min_tree:
                            return db_element

            if force_generation:
                nb_occurrences = 1

            for x in range(0, int(nb_occurrences)):
                db_elem_iter = {
                    'tag': 'sequence-iter',
                    'value': None,
                    'children': []
                }

                # generates the sequence
                for child in element:
                    if child.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
                        element_result = self.generate_element(child, xml_tree, choice_counter,
                                                               full_path=full_path, edit_data_tree=edit_data_tree,
                                                               schema_location=schema_location)

                        db_elem_iter['children'].append(element_result)
                    elif child.tag == "{0}sequence".format(LXML_SCHEMA_NAMESPACE):
                        sequence_result = self.generate_sequence(child, xml_tree, choice_counter,
                                                                 full_path=full_path, edit_data_tree=edit_data_tree,
                                                                 schema_location=schema_location)

                        db_elem_iter['children'].append(sequence_result)
                    elif child.tag == "{0}choice".format(LXML_SCHEMA_NAMESPACE):
                        choice_result = self.generate_choice(child, xml_tree, choice_counter,
                                                             full_path=full_path, edit_data_tree=edit_data_tree,
                                                             schema_location=schema_location)

                        db_elem_iter['children'].append(choice_result)
                    elif child.tag == "{0}any".format(LXML_SCHEMA_NAMESPACE):
                        pass
                    elif child.tag == "{0}group".format(LXML_SCHEMA_NAMESPACE):
                        pass

                db_element['children'].append(db_elem_iter)

        else:  # min_occurs == 1 and max_occurs == 1
            db_elem_iter = {
                'tag': 'sequence-iter',
                'value': None,
                'children': []
            }

            # XSD xpath
            # xsd_xpath = xml_tree.getpath(element)

            # init variables for buttons management
            nb_occurrences = 1  # nb of occurrences to render (can't be 0 or the user won't see this element at all)
            # nb_occurrences_data = min_occurs  # nb of occurrences in loaded data or in form being rendered (can be 0)

            if choice_counter is not None:
                if self.editing:
                    if nb_occurrences == 0:
                        if self.min_tree:
                            return db_element
                else:
                    if choice_counter > 0:
                        if self.min_tree:
                            return db_element

            # generates the sequence
            for child in element:
                if child.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
                    element_result = self.generate_element(child, xml_tree, choice_counter,
                                                           full_path=full_path, edit_data_tree=edit_data_tree,
                                                           schema_location=schema_location)

                    db_elem_iter['children'].append(element_result)
                elif child.tag == "{0}sequence".format(LXML_SCHEMA_NAMESPACE):
                    sequence_result = self.generate_sequence(child, xml_tree, choice_counter,
                                                             full_path=full_path, edit_data_tree=edit_data_tree,
                                                             schema_location=schema_location)

                    db_elem_iter['children'].append(sequence_result)
                elif child.tag == "{0}choice".format(LXML_SCHEMA_NAMESPACE):
                    choice_result = self.generate_choice(child, xml_tree, choice_counter,
                                                         full_path=full_path, edit_data_tree=edit_data_tree,
                                                         schema_location=schema_location)

                    db_elem_iter['children'].append(choice_result)
                elif child.tag == "{0}any".format(LXML_SCHEMA_NAMESPACE):
                    pass
                elif child.tag == "{0}group".format(LXML_SCHEMA_NAMESPACE):
                    pass

            db_element['children'].append(db_elem_iter)

        return db_element

    # FIXME: never called: see if still needed
    def generate_sequence_absent(self, element, xml_tree, schema_location=None):
        """ Generate data structure for an XML sequence absent from the tree

        Args:
            element:
            xml_tree:
            schema_location:

        Returns:

        """
        # TODO see if it can be merged in generate_sequence
        db_element = {
            'tag': 'sequence-iter',
            'value': None,
            'children': []
        }

        # TODO: needs to be tested
        if self.auto_key_keyref:
            self.init_key_keyref(element)

        # generates the sequence
        for child in element:
            if child.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
                element = self.generate_element(child, xml_tree, schema_location=schema_location)
                db_element['children'].append(element)
            elif child.tag == "{0}sequence".format(LXML_SCHEMA_NAMESPACE):
                sequence = self.generate_sequence(child, xml_tree, schema_location=schema_location)
                db_element['children'].append(sequence)
            elif child.tag == "{0}choice".format(LXML_SCHEMA_NAMESPACE):
                choice = self.generate_choice(child, xml_tree, schema_location=schema_location)
                db_element['children'].append(choice)
            elif child.tag == "{0}any".format(LXML_SCHEMA_NAMESPACE):
                pass
            elif child.tag == "{0}group".format(LXML_SCHEMA_NAMESPACE):
                pass

        return db_element

    def generate_choice(self, element, xml_tree, choice_counter=None, full_path="", edit_data_tree=None,
                        schema_location=None, force_generation=False):
        """ Generate data structure for an XML choice

        Args:
            element:
            xml_tree:
            choice_counter:
            full_path:
            edit_data_tree:
            schema_location:
            force_generation:

        Returns:

        """
        # (annotation?, (element|group|choice|sequence|any)*)
        # FIXME Group not supported
        # FIXME Choice not supported
        db_element = {
            'tag': 'choice',
            'options': {
                'xpath': {
                    'xsd': None,
                    'xml': full_path
                },
                'schema_location': schema_location
            },
            'value': None,
            'children': []
        }

        # init variables for buttons management
        nb_occurrences = 1  # nb of occurrences to render (can't be 0 or the user won't see this element at all)

        max_occurs = 1

        elements_found = None
        xml_element = None

        # not multiple roots
        # FIXME process differently this part
        if not isinstance(element, list):
            # XSD xpath: don't need it when multiple root (can't duplicate a root)
            xsd_xpath = xml_tree.getpath(element)

            db_element['options']['xpath']['xsd'] = xsd_xpath

            # get element's min/max occurs attributes
            min_occurs, max_occurs = get_element_occurrences(element)
            nb_occurrences_data = min_occurs  # nb of occurrences in loaded data or in form being rendered (can be 0)

            # loading data in the form
            if self.editing:
                # get the number of occurrences in the data
                download_enabled = self.download_dependencies
                elements_found = lookup_occurs(element, xml_tree, full_path, edit_data_tree,
                                               download_enabled=download_enabled)
                nb_occurrences_data = len(elements_found)
                if max_occurs != 1:
                    nb_occurrences_data = len(elements_found)
                else:
                    if len(elements_found) > 0:
                        nb_occurrences_data = 1

            if nb_occurrences_data > nb_occurrences:
                nb_occurrences = nb_occurrences_data

            # 'occurs' key contains the tuple (minOccurs, nbOccurs, maxOccurs)
            # db_element['options'] = (min_occurs, nb_occurrences_data, max_occurs)
            db_element['options']['min'] = min_occurs
            db_element['options']['max'] = max_occurs

        # keeps track of elements to display depending on the selected choice
        if choice_counter is not None:
            if self.editing:
                if nb_occurrences == 0:
                    if self.min_tree:
                        return db_element
            else:
                if choice_counter > 0:
                    if self.min_tree:
                        return db_element

        if force_generation:
            nb_occurrences = 1

        for x in range(0, int(nb_occurrences)):
            db_child = {
                'tag': 'choice-iter',
                'value': None,
                'children': []
            }

            element_found = None
            if elements_found is not None:
                try:
                    element_found = elements_found[x]
                except:
                    pass

            for (counter, choiceChild) in enumerate(list(element)):
                # For unbounded choice, explicitly don't generate the choices not selected
                if choiceChild.tag == "{0}element".format(LXML_SCHEMA_NAMESPACE):
                    # Find the default element
                    if choiceChild.attrib.get('name') is not None:
                        opt_label = choiceChild.attrib.get('name')
                    else:
                        opt_label = choiceChild.attrib.get('ref')

                        if ':' in choiceChild.attrib.get('ref'):
                            opt_label = opt_label.split(':')[1]

                    # get the schema namespaces
                    xml_tree_str = XSDTree.tostring(xml_tree)
                    namespaces = get_namespaces(xml_tree_str)
                    # add the XSI prefix used by extensions
                    namespaces['xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
                    target_namespace, target_namespace_prefix = get_target_namespace(xml_tree, namespaces)

                    if self.editing:
                        # TODO: manage unbounded choices for sequences/choices as well
                        if max_occurs != 1:
                            xml_element = False  # explicitly don't generate the element
                            element_path = opt_label if target_namespace is None else "{" + target_namespace + "}" + opt_label
                            if element_found is not None and element_found.tag == element_path:
                                xml_element = element_found  # explicitly build the element if found
                                db_child['value'] = counter

                        else:
                            # TODO: create prefix if no prefix?
                            element_path = get_xml_xpath(xml_tree, full_path, "element", opt_label, target_namespace,
                                                         target_namespace_prefix)
                            if len(edit_data_tree.xpath(element_path, namespaces=namespaces)) != 0:
                                db_child['value'] = counter
                    element_result = self.generate_element(choiceChild, xml_tree,
                                                           counter,
                                                           full_path=full_path,
                                                           edit_data_tree=edit_data_tree,
                                                           schema_location=schema_location,
                                                           xml_element=xml_element)

                    db_child_0 = element_result
                    db_child['children'].append(db_child_0)
                elif choiceChild.tag == "{0}group".format(LXML_SCHEMA_NAMESPACE):
                    pass
                elif choiceChild.tag == "{0}choice".format(LXML_SCHEMA_NAMESPACE):
                    choice = self.generate_choice(choiceChild, xml_tree,
                                                  counter, full_path=full_path,
                                                  edit_data_tree=edit_data_tree, schema_location=schema_location)

                    db_child['children'].append(choice)
                elif choiceChild.tag == "{0}sequence".format(LXML_SCHEMA_NAMESPACE):
                    sequence = self.generate_sequence(choiceChild, xml_tree,
                                                      counter, full_path=full_path,
                                                      edit_data_tree=edit_data_tree, schema_location=schema_location)

                    db_child_0 = sequence
                    db_child['children'].append(db_child_0)
                elif choiceChild.tag == "{0}any".format(LXML_SCHEMA_NAMESPACE):
                    pass

            db_element['children'].append(db_child)

        return db_element

    def generate_choice_absent(self, request, element_id, xsd_doc_data, renderer_class=ListRenderer):
        """ Generate data structure for an XML choice

        Args:
            request:
            element_id:
            xsd_doc_data:
            renderer_class:

        Returns:

        """
        element = data_structure_element_api.get_by_id(element_id)
        parents = data_structure_element_api.get_all_by_child_id(element_id)

        if self.auto_key_keyref:
            self.init_key_keyref(element)

        if len(parents) == 0:
            raise ValueError("No SchemaElement found")
        elif len(parents) > 1:
            raise ValueError("More than one SchemaElement found")

        parent = parents[0]

        schema_location = None
        if 'schema_location' in element.options:
            schema_location = element.options['schema_location']

        # if the xml element is from an imported schema
        if schema_location is not None:
            # open the imported file
            download_enabled = self.download_dependencies
            if download_enabled:
                ref_xml_schema_file = send_get_request(element.options['schema_location'])
                # get the content of the file
                ref_xml_schema_content = ref_xml_schema_file.content
                # build the XML tree
                xml_doc_tree = XSDTree.build_tree(ref_xml_schema_content)
                # get the namespaces from the imported schema
                namespaces = get_namespaces(ref_xml_schema_content)
            else:
                raise ParserError('Dependency could not be downloaded')
        else:
            # build the XML tree
            xml_doc_tree = XSDTree.build_tree(xsd_doc_data)
            # get the namespaces
            namespaces = get_namespaces(xsd_doc_data)

        # flatten the includes
        download_enabled = self.download_dependencies
        flattener = XSDFlattenerDatabaseOrURL(XSDTree.tostring(xml_doc_tree), download_enabled)
        xml_doc_tree_str = flattener.get_flat()
        xml_doc_tree = XSDTree.build_tree(xml_doc_tree_str)

        xpath_element = element.options['xpath']
        xsd_xpath = xpath_element['xsd']

        xml_xpath = None
        if 'xml' in xpath_element:
            xml_xpath = xpath_element['xml']

        xml_element = xml_doc_tree.xpath(xsd_xpath, namespaces=namespaces)[0]

        # FIXME: Support all possibilities
        if element.tag == 'element':
            # provide xpath without element name because already generated in generate_element
            db_tree = self.generate_element(xml_element, xml_doc_tree, full_path=xml_xpath.rsplit('/', 1)[0])
        elif element.tag == 'sequence':
            db_tree = self.generate_sequence(xml_element, xml_doc_tree, full_path=xml_xpath)
        else:
            raise ParserError('Element cannot be generated: not implemented.')

        # Saving the tree in MongoDB
        tree_root = load_schema_data_in_db(db_tree)

        # Replacing the children with the generated branch
        children = parent.children
        element_index = children.index(element)

        children[element_index] = tree_root

        parent.update(set__children=children)
        parent.update(set__value=str(tree_root.pk))

        parent.reload()

        renderer = renderer_class(tree_root, request)
        html_form = renderer.render(False)

        return html_form

    def generate_simple_type(self, element, xml_tree, full_path, edit_data_tree=None,
                             default_value=None, is_fixed=False, schema_location=None, implicit_extension=True):
        """ Generate data structure for an XML simple type

        Args:
            element:
            xml_tree:
            full_path:
            edit_data_tree:
            default_value:
            is_fixed:
            schema_location:
            implicit_extension:

        Returns:

        """
        # FIXME implement union, correct list
        db_element = {
            'tag': 'simple_type',
            'value': None,
            'children': [],
            'options': {
                'name': element.attrib['name'] if 'name' in element.attrib else '',
                'xmlns': get_element_namespace(element, xml_tree),
            },
        }

        # get namespace prefix to reference extension in xsi:type
        xml_tree_str = XSDTree.tostring(xml_tree)
        namespaces = get_namespaces(xml_tree_str)
        target_namespace, target_namespace_prefix = get_target_namespace(xml_tree, namespaces)
        ns_prefix = None
        if target_namespace is not None:
            for prefix, ns in namespaces.iteritems():
                if ns == target_namespace:
                    ns_prefix = prefix
                    break
        db_element['options']['ns_prefix'] = ns_prefix

        if not self.ignore_modules:
            if get_module_url(element) is not None:
                # XSD xpath: /element/complexType/sequence
                xsd_xpath = xml_tree.getpath(element)
                module = self.generate_module(element, xsd_xpath, full_path, xml_tree=xml_tree,
                                              edit_data_tree=edit_data_tree)

                db_element['children'].append(module)

                return db_element

        # check if the type has a name (can be referenced by an extension)
        if 'name' in element.attrib and implicit_extension:
            # check if types extend this one
            extensions = get_extensions(xml_tree, element.attrib['name'])

            # the type has some possible extensions
            if len(extensions) > 0:
                # add the base type that can be rendered alone without extensions
                extensions.insert(0, element)
                choice_content = self.generate_choice_extensions(extensions, xml_tree, None,
                                                                 full_path,
                                                                 edit_data_tree,
                                                                 default_value,
                                                                 is_fixed,
                                                                 schema_location)
                db_element['children'].append(choice_content)
                return db_element

        restriction_child = element.find('{0}restriction'.format(LXML_SCHEMA_NAMESPACE))
        if restriction_child is not None:
            restriction = self.generate_restriction(restriction_child, xml_tree, full_path,
                                                    edit_data_tree=edit_data_tree,
                                                    default_value=default_value,
                                                    is_fixed=is_fixed,
                                                    schema_location=schema_location)
            db_child = restriction
        else:
            list_child = element.find('{0}list'.format(LXML_SCHEMA_NAMESPACE))
            if list_child is not None:
                # TODO list can contain a restriction/enumeration
                # FIXME None default value
                if default_value is None:
                    default_value = ''

                db_child = {
                    'tag': 'list',
                    'value': default_value,
                    'children': []
                }
            else:
                union_child = element.find('{0}union'.format(LXML_SCHEMA_NAMESPACE))
                if union_child is not None:
                    # TODO: provide UI for unions
                    db_child = {
                        'tag': 'union',
                        'value': default_value,
                        'children': []
                    }
                else:
                    db_child = {
                        'tag': 'error'
                    }

        db_element['children'].append(db_child)

        return db_element

    def generate_complex_type(self, element, xml_tree, full_path, edit_data_tree=None, default_value='',
                              is_fixed=False, schema_location=None, implicit_extension=True):
        """ Generate data structure for an XML complex type

        Args:
            element:
            xml_tree:
            full_path:
            edit_data_tree:
            default_value:
            is_fixed:
            schema_location:
            implicit_extension:

        Returns:

        """
        # FIXME add support for complexContent, group, attributeGroup, anyAttribute
        # (
        #   annotation?,
        #   (
        #       simpleContent|complexContent|(
        #           (group|all|choice|sequence)?,
        #           (
        #               (attribute|attributeGroup)*,
        #               anyAttribute?
        #           )
        #       )
        #   )
        # )
        db_element = {
            'tag': 'complex_type',
            'value': None,
            'children': [],
            'options': {
                'name': element.attrib['name'] if 'name' in element.attrib else '',
                'xmlns': get_element_namespace(element, xml_tree),
            },
        }

        # get namespace prefix to reference extension in xsi:type
        xml_tree_str = XSDTree.tostring(xml_tree)
        namespaces = get_namespaces(xml_tree_str)
        target_namespace, target_namespace_prefix = get_target_namespace(xml_tree, namespaces)
        ns_prefix = None

        if target_namespace is not None:
            for prefix, ns in namespaces.iteritems():
                if ns == target_namespace:
                    ns_prefix = prefix
                    break

        db_element['options']['ns_prefix'] = ns_prefix

        if not self.ignore_modules:
            if get_module_url(element) is not None:
                # XSD xpath: /element/complexType/sequence
                xsd_xpath = xml_tree.getpath(element)
                module = self.generate_module(element, xsd_xpath, full_path, xml_tree=xml_tree,
                                              edit_data_tree=edit_data_tree)
                db_element['children'].append(module)

                return db_element

        # check if the type has a name (can be referenced by an extension)
        if 'name' in element.attrib and implicit_extension:
            # check if types extend this one
            extensions = get_extensions(xml_tree, element.attrib['name'])

            # the type has some possible extensions
            if len(extensions) > 0:
                # add the base type that can be rendered alone without extensions
                if self.implicit_extension_base:
                    extensions.insert(0, element)

                choice_content = self.generate_choice_extensions(extensions, xml_tree, None, full_path,
                                                                 edit_data_tree,
                                                                 default_value,
                                                                 schema_location)
                db_element['children'].append(choice_content)
                return db_element

        # is it a simple content?
        complex_type_child = element.find('{0}simpleContent'.format(LXML_SCHEMA_NAMESPACE))
        if complex_type_child is not None:
            result_simple_content = self.generate_simple_content(complex_type_child, xml_tree,
                                                                 full_path=full_path,
                                                                 edit_data_tree=edit_data_tree,
                                                                 default_value=default_value,
                                                                 is_fixed=is_fixed,
                                                                 schema_location=schema_location)
            db_element['children'].append(result_simple_content)

            return db_element

        # is it a complex content?
        complex_type_child = element.find('{0}complexContent'.format(LXML_SCHEMA_NAMESPACE))
        if complex_type_child is not None:
            complex_content_result = self.generate_complex_content(complex_type_child, xml_tree,
                                                                   full_path=full_path,
                                                                   edit_data_tree=edit_data_tree,
                                                                   default_value=default_value,
                                                                   schema_location=schema_location)
            db_element['children'].append(complex_content_result)

            return db_element

        # does it contain any attributes?
        complex_type_children = element.findall('{0}attribute'.format(LXML_SCHEMA_NAMESPACE))
        if len(complex_type_children) > 0:
            for attribute in complex_type_children:
                element_result = self.generate_element(attribute, xml_tree, full_path=full_path,
                                                       edit_data_tree=edit_data_tree, schema_location=schema_location)

                db_element['children'].append(element_result)
        # does it contain sequence or all?
        complex_type_child = element.find('{0}sequence'.format(LXML_SCHEMA_NAMESPACE))
        if complex_type_child is not None:
            sequence_result = self.generate_sequence(complex_type_child, xml_tree, full_path=full_path,
                                                     edit_data_tree=edit_data_tree, schema_location=schema_location)

            db_element['children'].append(sequence_result)
        else:
            complex_type_child = element.find('{0}all'.format(LXML_SCHEMA_NAMESPACE))
            if complex_type_child is not None:
                sequence_result = self.generate_sequence(complex_type_child, xml_tree, full_path=full_path,
                                                         edit_data_tree=edit_data_tree, schema_location=schema_location)

                db_element['children'].append(sequence_result)
            else:
                # does it contain choice ?
                complex_type_child = element.find('{0}choice'.format(LXML_SCHEMA_NAMESPACE))
                if complex_type_child is not None:
                    choice_result = self.generate_choice(complex_type_child, xml_tree, full_path=full_path,
                                                         edit_data_tree=edit_data_tree, schema_location=schema_location)

                    db_element['children'].append(choice_result)

        return db_element

    def generate_choice_extensions(self, element, xml_tree, choice_counter=None, full_path="",
                                   edit_data_tree=None, default_value='', is_fixed=False, schema_location=None):
        """ Generate data structure for an XML extension

        Args:
            element:
            xml_tree:
            choice_counter:
            full_path:
            edit_data_tree:
            default_value:
            is_fixed:
            schema_location:

        Returns:

        """
        db_element = {
            'tag': 'choice',
            'options': {
                'xpath': {
                    'xsd': None,
                    'xml': full_path
                },
                'schema_location': schema_location
            },
            'value': None,
            'children': []
        }

        # init variables for buttons management
        nb_occurrences = 1  # nb of occurrences to render (can't be 0 or the user won't see this element at all)

        # keeps track of elements to display depending on the selected choice
        if choice_counter is not None:
            if self.editing:
                if nb_occurrences == 0:
                    if self.min_tree:
                        return db_element
            else:
                if choice_counter > 0:
                    if self.min_tree:
                        return db_element

        # get the schema namespaces
        xml_tree_str = XSDTree.tostring(xml_tree)
        namespaces = get_namespaces(xml_tree_str)
        # add the XSI prefix used by extensions
        namespaces['xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        target_namespace, target_namespace_prefix = get_target_namespace(xml_tree, namespaces)

        # if root xsi:type
        if full_path == "":
            is_root = True
        else:
            is_root = False

        for x in range(0, int(nb_occurrences)):
            db_child = {
                'tag': 'choice-iter',
                'value': None,
                'children': [],
                'options': {},
            }

            for (counter, choiceChild) in enumerate(list(element)):

                if is_root:
                    if target_namespace_prefix != "":
                        full_path = "/{0}:{1}".format(target_namespace_prefix, choiceChild.attrib['name'])
                    else:
                        full_path = "/{0}".format(choiceChild.attrib['name'])

                if choiceChild.tag == "{0}simpleType".format(LXML_SCHEMA_NAMESPACE) or \
                        choiceChild.tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):

                    if choiceChild.tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):
                        result = self.generate_complex_type(choiceChild, xml_tree,
                                                            full_path=full_path,
                                                            edit_data_tree=edit_data_tree,
                                                            default_value=default_value,
                                                            is_fixed=is_fixed,
                                                            schema_location=schema_location,
                                                            implicit_extension=False)

                    elif choiceChild.tag == "{0}simpleType".format(LXML_SCHEMA_NAMESPACE):
                        result = self.generate_simple_type(choiceChild, xml_tree,
                                                           full_path=full_path,
                                                           edit_data_tree=edit_data_tree,
                                                           default_value=default_value,
                                                           is_fixed=is_fixed,
                                                           schema_location=schema_location,
                                                           implicit_extension=False)

                    # Find the default element
                    if choiceChild.attrib.get('name') is not None:
                        opt_label = choiceChild.attrib.get('name')
                    else:
                        opt_label = choiceChild.attrib.get('ref')

                        if ':' in choiceChild.attrib.get('ref'):
                            opt_label = opt_label.split(':')[1]

                    # look for active choice when editing
                    if self.editing:
                        ns_prefix = target_namespace_prefix + ":" if target_namespace is not None else ""
                        ns_element_path = '{0}[@xsi:type="{1}{2}"]'.format(full_path, ns_prefix, opt_label)
                        element_path = '{0}[@xsi:type="{1}"]'.format(full_path, opt_label)

                        ns_elements = edit_data_tree.xpath(ns_element_path, namespaces=namespaces)
                        elements = edit_data_tree.xpath(element_path, namespaces=namespaces)

                        if len(ns_elements) != 0 or len(elements) != 0:
                            db_child['value'] = counter

                    db_child['children'].append(result)

            db_element['children'].append(db_child)

        return db_element

    def generate_complex_content(self, element, xml_tree, full_path, edit_data_tree=None, default_value='',
                                 schema_location=None):
        """ Generate data structure for an XML complex content

        Args:
            element:
            xml_tree:
            full_path:
            edit_data_tree:
            default_value:
            schema_location:

        Returns:

        """
        # (annotation?,(restriction|extension))

        db_element = {
            'tag': 'complex_content',
            'value': None,
            'children': []
        }

        # generates the content
        restriction_child = element.find('{0}restriction'.format(LXML_SCHEMA_NAMESPACE))
        if restriction_child is not None:
            restriction_result = self.generate_restriction(restriction_child, xml_tree, full_path,
                                                           edit_data_tree=edit_data_tree,
                                                           default_value=default_value,
                                                           schema_location=schema_location)

            db_element['children'].append(restriction_result)
        else:
            extension_child = element.find('{0}extension'.format(LXML_SCHEMA_NAMESPACE))
            extension_result = self.generate_extension(extension_child, xml_tree, full_path,
                                                       edit_data_tree=edit_data_tree,
                                                       default_value=default_value,
                                                       schema_location=schema_location)

            db_element['children'].append(extension_result)

        return db_element

    def generate_module(self, element, xsd_xpath=None, xml_xpath=None, xml_tree=None, edit_data_tree=None):
        """ Generate data structure for a module

        Args:
            element:
            xsd_xpath:
            xml_xpath:
            xml_tree:
            edit_data_tree:

        Returns:

        """
        if self.ignore_modules:
            raise CoreError("Modules are not getting ignored even though they are turned off")

        db_element = {
            'tag': 'module',
            'value': None,
            'options': {
                'data': None,
                'attributes': None,
                'params': None,
                'multiple': False
            },
            'children': []
        }
        # FIXME: refactor get module url
        module_url = get_module_url(element)

        # check if a module is set for this element
        if module_url is not None:

            try:
                module = module_api.get_by_url(module_url.path)

                # add extra parameters coming from url parameters
                if module_url.query != '':
                    db_element['options']['params'] = dict(parse_qsl(module_url.query))

                db_element['options']['xpath'] = {
                    'xsd': xsd_xpath,
                    'xml': xml_xpath
                }

                db_element['options']['multiple'] = module.multiple

                # Get data to reload the module
                reload_data = None
                reload_attrib = None

                if self.editing:
                    # get the schema namespaces
                    xml_tree_str = XSDTree.tostring(xml_tree)
                    namespaces = get_namespaces(xml_tree_str)
                    edit_elements = edit_data_tree.xpath(xml_xpath, namespaces=namespaces)

                    if module.multiple:
                        reload_data = ""
                        for edit_element in edit_elements:
                            reload_data += XSDTree.tostring(edit_element)
                    else:
                        if len(edit_elements) > 0:
                            if len(edit_elements) == 1:
                                edit_element = edit_elements[0]

                                # get attributes
                                if 'attribute' not in xsd_xpath and len(edit_element.attrib) > 0:
                                    reload_attrib = dict(edit_element.attrib)

                                reload_data = get_xml_element_data(element, edit_element)
                            else:
                                raise ParserError("Unexpected number of elements found in the XML document.")

                db_element['options']['url'] = module_url.path
                db_element['options']['data'] = reload_data
                db_element['options']['attributes'] = reload_attrib
            except Exception, e:
                raise ParserError('Module not found.')

        return db_element

    def generate_simple_content(self, element, xml_tree, full_path='', edit_data_tree=None, default_value='',
                                is_fixed=False, schema_location=None):
        """ Generate data structure for an XML simple content

        Args:
            element:
            xml_tree:
            full_path:
            edit_data_tree:
            default_value:
            is_fixed:
            schema_location:

        Returns:

        """
        # (annotation?,(restriction|extension))
        # FIXME better support for extension

        db_element = {
            'tag': 'simple_content',
            'value': None,
            'children': []
        }

        # generates the content
        restriction_child = element.find('{0}restriction'.format(LXML_SCHEMA_NAMESPACE))
        if restriction_child is not None:
            restriction_result = self.generate_restriction(restriction_child, xml_tree, full_path,
                                                           edit_data_tree=edit_data_tree,
                                                           default_value=default_value,
                                                           is_fixed=is_fixed,
                                                           schema_location=schema_location)

            db_element['children'].append(restriction_result)
        else:
            extension_child = element.find('{0}extension'.format(LXML_SCHEMA_NAMESPACE))
            extension_result = self.generate_extension(extension_child, xml_tree, full_path,
                                                       edit_data_tree=edit_data_tree,
                                                       default_value=default_value,
                                                       is_fixed=is_fixed,
                                                       schema_location=schema_location)

            db_element['children'].append(extension_result)

        return db_element

    def generate_restriction(self, element, xml_tree, full_path="", edit_data_tree=None, default_value=None,
                             is_fixed=False, schema_location=None):
        """ Generate data structure for an XML restriction

        Args:
            element:
            xml_tree:
            full_path:
            edit_data_tree:
            default_value:
            is_fixed:
            schema_location:

        Returns:

        """
        # FIXME doesn't represent all the possibilities (http://www.w3schools.com/xml/el_restriction.asp)
        # FIXME simpleType is a possible child only if the base attr has not been specified
        db_element = {
            'tag': 'restriction',
            'options': {
                'base': element.attrib.get('base'),  # TODO Change it to avoid having the namespace with it
                'fixed': is_fixed
            },
            'value': None,
            'children': []
        }

        enumeration = element.findall('{0}enumeration'.format(LXML_SCHEMA_NAMESPACE))

        if len(enumeration) > 0:
            option_list = []

            if is_fixed:
                # Fixed
                for enum in enumeration:
                    db_child = {
                        'tag': 'enumeration',
                        'value': enum.attrib.get('value')
                    }

                    if enum.attrib.get('value') == default_value:
                        entry = (enum.attrib.get('value'), enum.attrib.get('value'), True)
                        db_element['value'] = default_value
                    else:
                        entry = (enum.attrib.get('value'), enum.attrib.get('value'), False)

                    option_list.append(entry)
                    db_element['children'].append(db_child)
            elif self.editing:
                # Edition
                default_value = default_value if default_value is not None else ''

                for enum in enumeration:
                    db_child = {
                        'tag': 'enumeration',
                        'value': enum.attrib.get('value')
                    }

                    if default_value is not None and enum.attrib.get('value') == default_value:
                        entry = (enum.attrib.get('value'), enum.attrib.get('value'), True)
                        db_element['value'] = default_value
                    else:
                        entry = (enum.attrib.get('value'), enum.attrib.get('value'), False)

                    option_list.append(entry)
                    db_element['children'].append(db_child)
            else:
                # New document
                for enum in enumeration:
                    db_child = {
                        'tag': 'enumeration',
                        'value': enum.attrib.get('value')
                    }

                    entry = (enum.attrib.get('value'), enum.attrib.get('value'), False)
                    option_list.append(entry)

                    db_element['children'].append(db_child)

                db_element['value'] = db_element['children'][0]['value']
        else:
            simple_type = element.find('{0}simpleType'.format(LXML_SCHEMA_NAMESPACE))
            if simple_type is not None:
                simple_type_result = self.generate_simple_type(simple_type, xml_tree,
                                                               full_path=full_path,
                                                               edit_data_tree=edit_data_tree,
                                                               default_value=default_value,
                                                               is_fixed=is_fixed,
                                                               schema_location=schema_location)

                db_child = simple_type_result
            else:
                # FIXME temp fix default value shouldn't be None
                if default_value is None:
                    default_value = ''

                db_child = {
                    'tag': 'input',
                    'value': default_value
                }

            db_element['children'].append(db_child)

        return db_element

    def generate_extension(self, element, xml_tree, full_path="", edit_data_tree=None, default_value='',
                           is_fixed=False, schema_location=None):
        """ Generate data structure for an XML extension

        Args:
            element:
            xml_tree:
            full_path:
            edit_data_tree:
            default_value:
            is_fixed:
            schema_location:

        Returns:

        """
        # FIXME doesn't represent all the possibilities (http://www.w3schools.com/xml/el_extension.asp)
        db_element = {
            'tag': 'extension',
            'value': None,
            'children': []
        }

        ##################################################
        # Parsing attributes
        #
        # 'base' (required) is the only attribute to parse
        ##################################################
        if 'base' in element.attrib:
            xml_tree_str = XSDTree.tostring(xml_tree)
            namespaces = get_namespaces(xml_tree_str)
            default_prefix = get_default_prefix(namespaces)

            target_namespace, target_namespace_prefix = get_target_namespace(xml_tree, namespaces)
            download_enabled = self.download_dependencies
            base_type, xml_tree, schema_location = get_element_type(element, xml_tree, namespaces, default_prefix,
                                                                    target_namespace_prefix, schema_location, 'base',
                                                                    download_enabled=download_enabled)

            # test if base is a built-in data types
            if not isinstance(base_type, etree._Element):
                db_element['children'].append(
                    {
                        'tag': 'input',
                        'value': default_value,
                        'options': {
                            'fixed': is_fixed,
                        }
                    }
                )
            else:  # not a built-in data type
                # fixed not allowed for extensions with base complex type
                if base_type.tag == "{0}complexType".format(LXML_SCHEMA_NAMESPACE):
                    complex_type_result = self.generate_complex_type(base_type, xml_tree,
                                                                     full_path=full_path,
                                                                     edit_data_tree=edit_data_tree,
                                                                     default_value=default_value,
                                                                     schema_location=schema_location,
                                                                     implicit_extension=False)

                    db_element['children'].append(complex_type_result)
                elif base_type.tag == "{0}simpleType".format(LXML_SCHEMA_NAMESPACE):
                    simple_type_result = self.generate_simple_type(base_type, xml_tree,
                                                                   full_path=full_path,
                                                                   edit_data_tree=edit_data_tree,
                                                                   default_value=default_value,
                                                                   is_fixed=is_fixed,
                                                                   schema_location=schema_location,
                                                                   implicit_extension=False)

                    db_element['children'].append(simple_type_result)

        ##################################################
        # Parsing children
        ##################################################
        if 'children' in db_element['children'][0]:  # Element extends simple or complex type
            extended_element = db_element['children'][0]['children']
        else:  # Element extends one of the base types
            extended_element = db_element['children']

        # does it contain any attributes?
        complex_type_children = element.findall('{0}attribute'.format(LXML_SCHEMA_NAMESPACE))
        if len(complex_type_children) > 0:
            for attribute in complex_type_children:
                element_result = self.generate_element(attribute, xml_tree,
                                                       full_path=full_path,
                                                       edit_data_tree=edit_data_tree,
                                                       schema_location=schema_location)

                # Attribute is pushed on top of the list of children
                extended_element.insert(0, element_result)

        # does it contain sequence or all?
        complex_type_child = element.find('{0}sequence'.format(LXML_SCHEMA_NAMESPACE))
        if complex_type_child is not None:
            sequence_result = self.generate_sequence(complex_type_child, xml_tree,
                                                     full_path=full_path,
                                                     edit_data_tree=edit_data_tree,
                                                     schema_location=schema_location)

            extended_element.append(sequence_result)
        else:
            complex_type_child = element.find('{0}all'.format(LXML_SCHEMA_NAMESPACE))
            if complex_type_child is not None:
                sequence_result = self.generate_sequence(complex_type_child, xml_tree,
                                                         full_path=full_path,
                                                         edit_data_tree=edit_data_tree,
                                                         schema_location=schema_location)

                extended_element.append(sequence_result)
            else:
                # does it contain choice ?
                complex_type_child = element.find('{0}choice'.format(LXML_SCHEMA_NAMESPACE))
                if complex_type_child is not None:
                    choice_result = self.generate_choice(complex_type_child, xml_tree,
                                                         full_path=full_path,
                                                         edit_data_tree=edit_data_tree,
                                                         schema_location=schema_location)

                    extended_element.append(choice_result)

        return db_element

    def is_key(self, element, full_path):
        """ Check if current element is used as a key

        Args:
            element:
            full_path:

        Returns:

        """
        # remove indexes from the xpath
        xpath = re.sub(r'\[[0-9]+\]', '', full_path)
        # remove namespaces
        for prefix in element.nsmap.keys():
            xpath = re.sub(r'{}:'.format(prefix), '', xpath)
        for key in self.keys.keys():
            if self.keys[key]['xpath'] == xpath:
                if self.keys[key]['module'] is not None:
                    add_appinfo_child_to_element(element, MODULE_TAG_NAME, self.keys[key]['module'])
                    return True
        return False

    def is_keyref(self, element, full_path):
        """ Check if current element is used as a keyref

        Args:
            element:
            full_path:

        Returns:

        """
        # remove indexes from the xpath
        xpath = re.sub(r'\[[0-9]+\]', '', full_path)
        # remove namespaces
        for prefix in element.nsmap.keys():
            xpath = re.sub(r'{}:'.format(prefix), '', xpath)
        for keyref in self.keyrefs.keys():
            if self.keyrefs[keyref]['xpath'] == xpath:
                add_appinfo_child_to_element(element, MODULE_TAG_NAME, 'module-auto-keyref?keyref={}'.format(keyref))
                return True
        return False

    def manage_key_keyref(self, element, full_path):
        """ Collect key and keyref elements

        Args:
            element:
            full_path:

        Returns:

        """
        # get keys in element scope
        list_key = element.findall('{0}key'.format(LXML_SCHEMA_NAMESPACE))
        # get keyrefs in element scope
        list_keyref = element.findall('{0}keyref'.format(LXML_SCHEMA_NAMESPACE))

        # remove indexes from the xpath
        full_path = re.sub(r'\[[0-9]+\]', '', full_path)

        if len(list_key) > 0:
            for key in list_key:
                key_name = key.attrib['name']
                # print key_name

                selector = key.find('{0}selector'.format(LXML_SCHEMA_NAMESPACE))
                selector_xpath = selector.attrib['xpath']
                key_selector = full_path + '/' + selector_xpath
                # remove namespaces
                for prefix in selector.nsmap.keys():
                    key_selector = re.sub(r'{}:'.format(prefix), '', key_selector)
                # print key_selector

                # FIXME: manage multiple fields
                fields = key.findall('{0}field'.format(LXML_SCHEMA_NAMESPACE))
                for field in fields:
                    field_xpath = field.attrib['xpath']
                    key_field = key_selector + '/' + field_xpath
                    # print key_field

                # look if a module is attached to the key
                module_url = get_module_url(key)
                if module_url is not None:
                    module = "{0}?key={1}".format(module_url.path, key_name)
                else:
                    module = None

                self.keys[key_name] = {'xpath': key_field,
                                       'module_ids': [],
                                       'module': module}

            for keyref in list_keyref:
                keyref_name = keyref.attrib['name']
                keyref_refer = keyref.attrib['refer']
                if ':' in keyref_refer:
                    keyref_refer = keyref_refer.split(':')[1]

                selector = keyref.find('{0}selector'.format(LXML_SCHEMA_NAMESPACE))
                selector_xpath = selector.attrib['xpath']
                keyref_selector = full_path + '/' + selector_xpath
                # remove namespaces
                for prefix in selector.nsmap.keys():
                    keyref_selector = re.sub(r'{}:'.format(prefix), '', keyref_selector)

                # FIXME: manage multiple fields
                fields = keyref.findall('{0}field'.format(LXML_SCHEMA_NAMESPACE))
                for field in fields:
                    field_xpath = field.attrib['xpath']
                    keyref_field = keyref_selector + '/' + field_xpath

                self.keyrefs[keyref_name] = {'xpath': keyref_field,
                                             'refer': keyref_refer,
                                             'module_ids': []}

    def init_key_keyref(self, element):
        """ Initialize keys and keyrefs

        Args:
            element:

        Returns:

        """
        root = data_structure_element_api.get_root_element(element)
        if 'keys' in root.options:
            self.keys = root.options['keys']
        if 'keyrefs' in root.options:
            self.keyrefs = root.options['keyrefs']
