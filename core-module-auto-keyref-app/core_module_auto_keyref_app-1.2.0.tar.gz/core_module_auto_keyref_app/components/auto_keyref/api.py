""" AutoKeyref apis
"""
from core_module_auto_keyref_app.components.auto_keyref.models import AutoKeyref


def upsert(auto_keyref):
    """ Save or update AutoKeyref

    Args:
        auto_keyref:

    Returns:

    """
    return auto_keyref.save()


def get_by_root(root):
    """ Get AutoKeyref by root element

    Args:
        root:

    Returns:

    """
    return AutoKeyref.get_by_root(root)
