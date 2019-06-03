""" Curate data Structure api
"""
from core_curate_app.components.curate_data_structure.models import CurateDataStructure


def upsert(curate_data_structure):
    """ Save or update the Curate Data Structure

    Args:
        curate_data_structure:

    Returns:

    """
    return curate_data_structure.save_object()


def get_none():
    """ Returns None object, used by forms

    Returns:

    """
    return CurateDataStructure.get_none()


def get_all():
    """ Returns all curate data structure api

    Returns:

    """
    return CurateDataStructure.get_all()


def get_by_id(curate_data_structure_id):
    """ Returns the curate data structure with the given id

    Args:
        curate_data_structure_id:

    Returns:

    """
    return CurateDataStructure.get_by_id(curate_data_structure_id)


def get_all_by_user_id_and_template_id(user_id, template_id):
    """ Returns object with the given user id and template id

    Args:
        user_id:
        template_id:

    Returns:

    """
    return CurateDataStructure.get_all_by_user_id_and_template_id(user_id, template_id)


def get_by_user_id_and_template_id_and_name(user_id, template_id, name):
    """ Returns object with the given user id and template id and name

    Args:
        user_id:
        template_id:
        name:

    Returns:

    """
    return CurateDataStructure.get_by_user_id_and_template_id_and_name(user_id, template_id, name)


def delete(curate_data_structure):
    """ Deletes the curate data structure and the element associated

    Args:
        curate_data_structure:
    """
    curate_data_structure.delete()


def get_all_by_user_id_with_no_data(user_id):
    """ Returns all the curate date structure of the user, with no data.

    Args: user_id:
    Returns:
    """
    return CurateDataStructure.get_all_by_user_id_with_no_data(user_id)


def get_all_except_user_id_with_no_data(user_id):
    """ Returns all the curate date structure except the one of the user, with no data.

    Args: user_id:
    Returns:
    """
    return CurateDataStructure.get_all_except_user_id_with_no_data(user_id)


def get_all_by_user_id_and_template_id_with_no_data(user_id, template_id):
    """ Return all the curate data structure by user and template, with no link to a data

    Args:
        user_id:
        template_id:

    Returns:

    """
    return CurateDataStructure.get_all_by_user_id_and_template_id_with_no_data(user_id, template_id)


def get_all_with_no_data():
    """ Returns all curate data structure api with no link to a data.

    Returns:

    """
    return CurateDataStructure.get_all_with_no_data()


def get_by_data_id(data_id):
    """ Return the curate data structure with the given data id

    Args:
        data_id:

    Returns:

    """
    return CurateDataStructure.get_by_data_id(data_id)


def update_data_structure_root(curate_data_structure, root_element):
    """Update the data structure with a root element.

    Args:
        curate_data_structure:
        root_element:

    Returns:

    """
    # Delete data structure elements
    curate_data_structure.delete_data_structure_elements_from_root()

    # set the root element in the data structure
    curate_data_structure.data_structure_element_root = root_element

    # save the data structure
    return upsert(curate_data_structure)
