#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Search transaction rendering methods."""
from six import text_type
from .base import SearchBase


class KeysRender(SearchBase):
    """Render an insitution for search."""

    fields = [
        'obj_id', 'display_name', 'keyword', 'release',
        'updated_date', 'created_date'
    ]

    @staticmethod
    def obj_id(**key_obj):
        """Return string for object id."""
        return text_type('keys_{_id}').format(**key_obj)

    @staticmethod
    def updated_date(**key_obj):
        """Return string for the updated date."""
        return text_type('{updated}').format(**key_obj)

    @staticmethod
    def created_date(**key_obj):
        """Return string for the created date."""
        return text_type('{created}').format(**key_obj)

    @staticmethod
    def display_name(**key_obj):
        """Return the string to render display_name."""
        return text_type('{display_name}').format(**key_obj)

    @staticmethod
    def keyword(**key_obj):
        """Return the rendered string for keywords."""
        return text_type('{key}').format(**key_obj)

    @classmethod
    def release(cls, **_key_obj):
        """Return whether the user has released anything."""
        return 'true'

    @classmethod
    def get_transactions(cls, **_kwargs):
        """Just return an empty array."""
        return []
