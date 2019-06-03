"""API for Data Structure Element
"""
from core_main_app.commons.exceptions import DoesNotExist
from core_parser_app.components.data_structure_element.models import DataStructureElement


def upsert(data_structure_element):
    """ Save or update the Data Structure Element

    Args:
        data_structure_element:

    Returns:

    """
    return data_structure_element.save()


def get_all():
    """ List all DataStructureElement

        Returns: DataStructureElement collection
    """
    return DataStructureElement.get_all()


def get_all_by_child_id(child_id):
    """ Get Data structure element object which contains the given child id in its children

    Args:
        child_id:

    Returns:

    """
    return DataStructureElement.get_all_by_child_id(child_id)


def get_by_id(data_structure_element_id):
    """ Return DataStructureElement object with the given id

        Args:
            data_structure_element_id:

        Returns: DataStructureElement object
    """
    return DataStructureElement.get_by_id(data_structure_element_id)


# TODO: needs to be reworked
def pull_children(data_structure_element, children):
    """

    Args:
        data_structure_element:
        children:

    Returns:

    """
    data_structure_element.update(pull__children=children)
    data_structure_element.reload()


# TODO: needs to be reworked
def add_to_set(data_structure_element, children):
    """

    Args:
        data_structure_element:
        children:

    Returns:

    """
    data_structure_element.update(add_to_set__children=children)
    data_structure_element.reload()


def get_root_element(data_structure_element):
    """ Return element's root

    Args:
        data_structure_element:

    Returns:

    """
    current_element = data_structure_element
    parent_list = get_all_by_child_id(current_element.id)
    while len(parent_list) > 0:
        current_element = parent_list[0]
        parent_list = get_all_by_child_id(current_element.id)

    return current_element
