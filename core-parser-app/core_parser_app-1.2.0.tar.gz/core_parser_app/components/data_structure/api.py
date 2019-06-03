"""Data structure api
"""

from core_parser_app.components.data_structure.models import DataStructure


def get_by_id(data_structure_id):
    """ Return the data structure with the given id

    Args:
        data_structure_id:

    Returns:

    """
    return DataStructure.get_by_id(data_structure_id)
