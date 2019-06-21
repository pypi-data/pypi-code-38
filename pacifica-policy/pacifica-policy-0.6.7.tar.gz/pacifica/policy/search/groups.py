#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Search transaction rendering methods."""
from six import text_type
from .base import SearchBase


class GroupsRender(SearchBase):
    """Render an insitution for search."""

    fields = [
        'obj_id', 'display_name', 'keyword', 'release',
        'updated_date', 'created_date'
    ]

    @staticmethod
    def obj_id(**group_obj):
        """Return string for object id."""
        return text_type('groups_{_id}').format(**group_obj)

    @staticmethod
    def updated_date(**group_obj):
        """Return string for the updated date."""
        return text_type('{updated}').format(**group_obj)

    @staticmethod
    def created_date(**group_obj):
        """Return string for the created date."""
        return text_type('{created}').format(**group_obj)

    @staticmethod
    def display_name(**group_obj):
        """Return the string to render display_name."""
        return text_type('{display_name}').format(**group_obj)

    @staticmethod
    def keyword(**group_obj):
        """Return the rendered string for keywords."""
        return text_type('{name}').format(**group_obj)

    @classmethod
    def release(cls, **_group_obj):
        """Return whether the user has released anything."""
        return 'true'

    @classmethod
    def get_transactions(cls, **_group_obj):
        """Just return an empty list."""
        return []
