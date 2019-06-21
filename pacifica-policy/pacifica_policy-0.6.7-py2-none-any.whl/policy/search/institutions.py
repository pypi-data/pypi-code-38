#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Search transaction rendering methods."""
from six import text_type
from .users import UsersRender
from .base import SearchBase


class InstitutionsRender(SearchBase):
    """Render an insitution for search."""

    fields = [
        'obj_id', 'display_name', 'keyword', 'release',
        'updated_date', 'created_date'
    ]

    @staticmethod
    def obj_id(**inst_obj):
        """Return string for object id."""
        return text_type('institutions_{_id}').format(**inst_obj)

    @staticmethod
    def updated_date(**inst_obj):
        """Return string for the updated date."""
        return text_type('{updated}').format(**inst_obj)

    @staticmethod
    def created_date(**inst_obj):
        """Return string for the created date."""
        return text_type('{created}').format(**inst_obj)

    @staticmethod
    def display_name(**inst_obj):
        """Return the string to render display_name."""
        return text_type('{name}').format(**inst_obj)

    @staticmethod
    def keyword(**inst_obj):
        """Return the rendered string for keywords."""
        return text_type('{name}').format(**inst_obj)

    @classmethod
    def release(cls, **_inst_obj):
        """Return whether the user has released anything."""
        return 'true'

    @classmethod
    def get_transactions(cls, **inst_obj):
        """Return the list of transaction ids for the user."""
        ret = set()
        for inst_user_obj in cls.get_rel_by_args('institution_user', institution=inst_obj['_id']):
            ret.update(UsersRender.get_transactions(_id=inst_user_obj['user']))
        return [
            'transactions_{}'.format(trans_id)
            for trans_id in ret
        ]
