""" Autokey apis
"""
from core_module_auto_key_app.components.auto_key.models import AutoKey


def upsert(auto_key):
    """ Save or update AutoKey

    Args:
        auto_key:

    Returns:

    """
    return auto_key.save()


def get_by_root(root):
    """ Get AutoKey by root element

    Args:
        root:

    Returns:

    """
    return AutoKey.get_by_root(root)
