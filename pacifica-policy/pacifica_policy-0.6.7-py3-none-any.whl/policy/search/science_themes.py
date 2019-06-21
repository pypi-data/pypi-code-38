#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Search transaction rendering methods."""
from six import text_type
from .base import SearchBase


class ScienceThemesRender(SearchBase):
    """Render an insitution for search."""

    fields = [
        'obj_id', 'display_name', 'keyword', 'release',
        'updated_date', 'created_date'
    ]

    @staticmethod
    def obj_id(**proj_obj):
        """Return string for object id."""
        return text_type('science_themes_{science_theme}').format(**proj_obj)

    @staticmethod
    def updated_date(**proj_obj):
        """Return string for the updated date."""
        return text_type('{updated}').format(**proj_obj)

    @staticmethod
    def created_date(**proj_obj):
        """Return string for the created date."""
        return text_type('{created}').format(**proj_obj)

    @staticmethod
    def display_name(**proj_obj):
        """Return the string to render display_name."""
        return text_type('{science_theme}').format(**proj_obj)

    @staticmethod
    def keyword(**proj_obj):
        """Return the rendered string for keywords."""
        return text_type('{science_theme}').format(**proj_obj)

    @classmethod
    def release(cls, **_proj_obj):
        """Return whether the user has released anything."""
        return 'true'

    @classmethod
    def get_transactions(cls, **proj_obj):
        """Return the list of transaction ids for the user."""
        ret = set()
        for rel_proj_obj in cls.get_rel_by_args('projects', science_theme=proj_obj['science_theme']):
            ret.update([
                'transactions_{}'.format(trans_id)
                for trans_id in cls._transsip_transsap_merge({'project': rel_proj_obj['_id']}, '_id')
            ])
        return list(ret)
