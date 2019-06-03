"""Saved Query API
"""
from core_explore_example_app.components.saved_query.models import SavedQuery


def get_all():
    """Get all Saved Query

    Returns:

    """
    return SavedQuery.get_all()


def get_by_id(query_id):
    """Get a Saved Query

    Args:
        query_id:

    Returns:

    """
    return SavedQuery.get_by_id(query_id)


def get_all_by_user_and_template(user_id, template_id):
    """Gets a saved query by user id and template id

    Args:
        user_id:
        template_id:

    Returns:

    """
    return SavedQuery.get_all_by_user_and_template(user_id, template_id)


def delete(saved_query):
    """Deletes a saved query

    Args:
        saved_query:

    Returns:

    """
    saved_query.delete()


def upsert(saved_query):
    """Saves or Updates a saved query

    Args:
        saved_query:

    Returns:

    """
    return saved_query.save()

