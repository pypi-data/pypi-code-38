"""Parser util for explore app
"""
from core_explore_example_app.settings import PARSER_DOWNLOAD_DEPENDENCIES
from core_explore_example_app.utils.custom_checkbox_renderer import CustomCheckboxRenderer
from core_parser_app.components.data_structure_element import api as data_structure_element_api
from core_parser_app.tools.parser.parser import XSDParser, remove_child_element


# TODO: the form renders 'add' buttons based on maxOccurs attributes, but we don't need more than one of each element


def get_parser():
    """Returns parser

    Returns:

    """

    return XSDParser(min_tree=True,
                     ignore_modules=True,
                     collapse=True,
                     auto_key_keyref=False,
                     implicit_extension_base=False,
                     download_dependencies=PARSER_DOWNLOAD_DEPENDENCIES,
                     store_type=True)


# FIXME: refactor common code with core curate app (note: no xml_string here)
def generate_form(xsd_string):
    """Generates the form using the parser, returns the root element

    Args:
        xsd_string:

    Returns:

    """
    # build parser
    parser = get_parser()
    # generate form
    root_element_id = parser.generate_form(xsd_string)
    # get the root element
    root_element = data_structure_element_api.get_by_id(root_element_id)

    return root_element


def render_form(request, root_element):
    """Renders the form

    Args:
        request:
        root_element:

    Returns:

    """
    # build a renderer
    renderer = CustomCheckboxRenderer(root_element, request)
    # render the form
    xsd_form = renderer.render()

    return xsd_form


def generate_element_absent(request, element_id, xsd_string):
    """ Generate an element absent from the form

    Args:
        request:
        element_id:
        xsd_string:

    Returns:

    """
    xsd_parser = get_parser()
    html_form = xsd_parser.generate_element_absent(request,
                                                   element_id,
                                                   xsd_string,
                                                   renderer_class=CustomCheckboxRenderer)
    return html_form


def generate_choice_absent(request, element_id, xsd_string):
    """ Generate a choice branch absent from the form

    Args:
        request:
        element_id:
        xsd_string:

    Returns:

    """
    xsd_parser = get_parser()
    html_form = xsd_parser.generate_choice_absent(request,
                                                  element_id,
                                                  xsd_string,
                                                  renderer_class=CustomCheckboxRenderer)
    return html_form


# TODO: need to be reworked + similar as code in curate app
def remove_form_element(request, element_id):
    """ Remove an element from the form.

    Args:
        request:
        element_id:

    Returns:

    """
    element_list = data_structure_element_api.get_all_by_child_id(element_id)

    if len(element_list) == 0:
        raise ValueError("No Data Structure Element found")
    elif len(element_list) > 1:
        raise ValueError("More than one Data Structure Element found")

    # Removing the element from the data structure
    data_structure_element = element_list[0]
    data_structure_element_to_pull = data_structure_element_api.get_by_id(element_id)

    # number of children after deletion
    children_number = len(data_structure_element.children) - 1

    data_structure_element = remove_child_element(data_structure_element,
                                                  data_structure_element_to_pull)

    code = 0
    html_form = ""

    if children_number <= data_structure_element.options['min']:
        # len(schema_element.children) == schema_element.options['min']
        if data_structure_element.options['min'] != 0:
            code = 1
        else:  # schema_element.options['min'] == 0
            code = 2
            renderer = CustomCheckboxRenderer(data_structure_element, request)
            html_form = renderer.render(True)

    return code, html_form
