#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Search transaction rendering methods."""
from six import text_type
from .base import SearchBase


class RelationshipsRender(SearchBase):
    """Render an insitution for search."""

    fields = [
        'obj_id', 'name', 'display_name', 'keyword',
        'updated_date', 'created_date'
    ]

    @staticmethod
    def obj_id(**rel_obj):
        """Return string for object id."""
        return text_type('relationships_{uuid}').format(**rel_obj)

    @staticmethod
    def updated_date(**rel_obj):
        """Return string for the updated date."""
        return text_type('{updated}').format(**rel_obj)

    @staticmethod
    def created_date(**rel_obj):
        """Return string for the created date."""
        return text_type('{created}').format(**rel_obj)

    @staticmethod
    def display_name(**rel_obj):
        """Return the string to render display_name."""
        return text_type('{display_name}').format(**rel_obj)

    @staticmethod
    def keyword(**rel_obj):
        """Return the rendered string for keywords."""
        return text_type('{display_name}').format(**rel_obj)

    @classmethod
    def name(cls, **rel_obj):
        """Return whether the user has released anything."""
        return text_type('{name}').format(**rel_obj)

    @classmethod
    def get_transactions(cls, **_kwargs):
        """Just return an empty list."""
        return []
