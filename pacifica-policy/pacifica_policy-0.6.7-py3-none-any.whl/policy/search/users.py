#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Search transaction rendering methods."""
from six import text_type
from .base import SearchBase


class UsersRender(SearchBase):
    """Render a transaction for search."""

    fields = [
        'obj_id', 'display_name', 'keyword', 'release',
        'updated_date', 'created_date'
    ]

    @staticmethod
    def obj_id(**user_obj):
        """Return string for object id."""
        return text_type('users_{_id}').format(**user_obj)

    @staticmethod
    def updated_date(**user_obj):
        """Return string for the updated date."""
        return text_type('{updated}').format(**user_obj)

    @staticmethod
    def created_date(**user_obj):
        """Return string for the created date."""
        return text_type('{created}').format(**user_obj)

    @staticmethod
    def display_name(**user_obj):
        """Return the string to render display_name."""
        return text_type('{last_name}, {first_name} {middle_initial}').format(**user_obj)

    @staticmethod
    def keyword(**user_obj):
        """Return the rendered string for keywords."""
        return text_type('{last_name}, {first_name} {middle_initial}').format(**user_obj)

    @classmethod
    def release(cls, **user_obj):
        """Return whether the user has released anything."""
        for trans_id in cls._transsip_transsap_merge({'submitter': user_obj['_id']}, '_id'):
            if cls.get_rel_by_args('transaction_user', transaction=trans_id, relationship=cls.releaser_uuid):
                return 'true'
        return 'false'

    @classmethod
    def get_transactions(cls, **user_obj):
        """Return the list of transaction ids for the user."""
        return [
            'transactions_{}'.format(trans_id)
            for trans_id in cls._transsip_transsap_merge({'submitter': user_obj['_id']}, '_id')
        ]
