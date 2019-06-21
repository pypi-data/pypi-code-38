#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Search transaction rendering methods."""
from six import text_type
from .base import SearchBase


class ValuesRender(SearchBase):
    """Render an insitution for search."""

    fields = [
        'obj_id', 'display_name', 'keyword', 'release',
        'updated_date', 'created_date'
    ]

    @staticmethod
    def obj_id(**value_obj):
        """Return string for object id."""
        return text_type('values_{_id}').format(**value_obj)

    @staticmethod
    def updated_date(**value_obj):
        """Return string for the updated date."""
        return text_type('{updated}').format(**value_obj)

    @staticmethod
    def created_date(**value_obj):
        """Return string for the created date."""
        return text_type('{created}').format(**value_obj)

    @staticmethod
    def display_name(**value_obj):
        """Return the string to render display_name."""
        return text_type('{display_name}').format(**value_obj)

    @staticmethod
    def keyword(**value_obj):
        """Return the rendered string for keywords."""
        return text_type('{value}').format(**value_obj)

    @classmethod
    def release(cls, **_value_obj):
        """Return whether the user has released anything."""
        return 'true'

    @classmethod
    def get_transactions(cls, **_kwargs):
        """Just return empty for this."""
        return []
