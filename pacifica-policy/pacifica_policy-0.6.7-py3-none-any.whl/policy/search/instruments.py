#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Search transaction rendering methods."""
from six import text_type
from .keys import KeysRender
from .values import ValuesRender
from .base import SearchBase


class InstrumentsRender(SearchBase):
    """Render an insitution for search."""

    fields = [
        'obj_id', 'display_name', 'keyword', 'release',
        'updated_date', 'created_date'
    ]
    rel_objs = ['key_value_pairs']

    @staticmethod
    def obj_id(**instrument_obj):
        """Return string for object id."""
        return text_type('instruments_{_id}').format(**instrument_obj)

    @staticmethod
    def updated_date(**instrument_obj):
        """Return string for the updated date."""
        return text_type('{updated}').format(**instrument_obj)

    @staticmethod
    def created_date(**instrument_obj):
        """Return string for the created date."""
        return text_type('{created}').format(**instrument_obj)

    @staticmethod
    def display_name(**instrument_obj):
        """Return the string to render display_name."""
        return text_type('{display_name}').format(**instrument_obj)

    @staticmethod
    def keyword(**instrument_obj):
        """Return the rendered string for keywords."""
        return text_type('{name}').format(**instrument_obj)

    @classmethod
    def release(cls, **_instrument_obj):
        """Return whether the user has released anything."""
        return 'true'

    @classmethod
    def key_value_pairs_obj_lists(cls, **inst_obj):
        """Get the key value pairs related to the transaction."""
        ret = {
            'key_value_hash': {},
            'key_objs': [],
            'value_objs': []
        }
        inst_kvp_objs = cls.get_rel_by_args(
            'instrument_key_value',
            instrument=inst_obj['_id'],
            relationship=cls.search_required_uuid
        )
        for inst_kvp_obj in inst_kvp_objs:
            key_obj = cls.get_rel_by_args('keys', _id=inst_kvp_obj['key'])[0]
            value_obj = cls.get_rel_by_args('values', _id=inst_kvp_obj['value'])[0]
            ret['key_objs'].append(KeysRender.render(key_obj))
            ret['value_objs'].append(ValuesRender.render(value_obj))
            ret['key_value_hash'][key_obj['key']] = value_obj['value']
        return ret

    # this doesn't get executed but is needed to be here to satisfy abstract method
    @classmethod
    def get_transactions(cls, **inst_obj):
        """Return the list of transaction ids for the user."""
        return [
            'transactions_{}'.format(transsip_obj['_id'])
            for transsip_obj in cls.get_rel_by_args('transsip', instrument=inst_obj['_id'])
        ]
