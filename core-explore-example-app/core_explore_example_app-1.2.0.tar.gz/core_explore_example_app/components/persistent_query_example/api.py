""" Persistent Query Example API
"""
from core_explore_example_app.components.persistent_query_example.models import PersistentQueryExample


def get_by_id(persistent_query_example_id):
    """ Return the Persistent Query Example with the given id

    Args:
        persistent_query_example_id:

    Returns:

    """
    return PersistentQueryExample.get_by_id(persistent_query_example_id)
