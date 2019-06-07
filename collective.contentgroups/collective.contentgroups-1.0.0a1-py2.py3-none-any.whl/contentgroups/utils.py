# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import base_hasattr
from six import string_types


def list_users(obj):
    """List users from object.

    obj can be a Plone content item, or it can be a simple string.
    """
    if isinstance(obj, string_types):
        users = obj
    else:
        if not base_hasattr(obj, "users"):
            return []
        users = obj.users
    if not users:
        return []
    return sorted(filter(None, [line.strip() for line in users.splitlines()]))
