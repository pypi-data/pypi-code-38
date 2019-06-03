""" Persistent Query Example API
"""
from core_explore_keyword_app.components.persistent_query_keyword.models import PersistentQueryKeyword


def get_by_id(persistent_query_keyword_id):
    """ Return the Persistent Query Keyword with the given id

    Args:
        persistent_query_keyword_id:

    Returns:

    """
    return PersistentQueryKeyword.get_by_id(persistent_query_keyword_id)
