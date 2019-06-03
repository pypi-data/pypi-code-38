""" Explore data Structure api
"""
from core_explore_example_app.components.explore_data_structure.models import ExploreDataStructure
from core_explore_example_app.utils.parser import generate_form


def get_by_user_id_and_template_id(user_id, template_id):
    """ Returns object with the given user id and template id

    Args:
        user_id:
        template_id:

    Returns:

    """
    return ExploreDataStructure.get_by_user_id_and_template_id(user_id, template_id)


def upsert(explore_data_structure):
    """Saves explore data structure

    Args:
        explore_data_structure:

    Returns:

    """
    return explore_data_structure.save()


def create_and_get_explore_data_structure(template, user_id):
    """ Get Data structure from template and user, generate them if no exist

    Args:
        template:
        user_id:

    Returns: Explore Data structure

    """
    try:
        # get data structure
        explore_data_structure = get_by_user_id_and_template_id(user_id=str(user_id),
                                                                template_id=template.id)
    except:
        # generate the root element
        root_element = generate_form(template.content)
        # create explore data structure
        explore_data_structure = ExploreDataStructure(user=str(user_id),
                                                      template=template,
                                                      name=template.filename,
                                                      data_structure_element_root=root_element)

        # save the data structure
        upsert(explore_data_structure)

    # Return the data structure
    return explore_data_structure


def get_by_id(explore_data_structure_id):
    """ Return the explore data structure with the given id

    Args:
        explore_data_structure_id:

    Returns:

    """
    return ExploreDataStructure.get_by_id(explore_data_structure_id)
