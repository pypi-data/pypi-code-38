"""XML utils
"""
from core_main_app.commons.exceptions import XMLError
from xml_utils.xsd_types.xsd_types import get_xsd_floating_numbers, get_xsd_numbers


def validate_element_value(element_name, element_type, element_value, namespace_prefix):
    """Validates the element

    Args:
        element_name:
        element_type:
        element_value:
        namespace_prefix:

    Returns:

    """
    error = None

    # Floating number
    if element_type in get_xsd_floating_numbers(namespace_prefix):
        try:
            float(element_value)
        except ValueError:
            error = "Element {} must be a number.".format(element_name)
    # Number
    elif element_type in get_xsd_numbers(namespace_prefix):
        try:
            int(element_value)
        except ValueError:
            error = "Element {} must be an integer.".format(element_name)

    return error


def get_enumerations(data_structure_element):
    """

    Args:
        data_structure_element:

    Returns:

    """
    # find child simple type
    try:
        while data_structure_element.tag != 'simple_type':
            data_structure_element = data_structure_element.children[0]
        simple_type_element = data_structure_element.children[0]
    except:
        raise XMLError("Unable to find a simple type for the data structure element.")

    enums = []
    for enum_element in simple_type_element.children:
        if enum_element.tag == 'enumeration':
            enums.append(enum_element.value)
    return enums
