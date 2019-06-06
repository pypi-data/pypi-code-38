#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the keys ORM object."""
from json import dumps
from pacifica.metadata.orm.keys import Keys
from .base_test import TestBase

SAMPLE_KEY_HASH = {
    '_id': 127,
    'key': 'Test Key 1',
    'display_name': 'Test Key 1',
    'description': 'Test Key 1',
    'encoding': 'UTF8'
}

SAMPLE_UNICODE_KEY_HASH = {
    '_id': 127,
    'key': u'Tést Key 2',
    'display_name': u'Tést Key 2',
    'description': u'Tést Key 2',
    'encoding': 'UTF8'
}


class TestKeys(TestBase):
    """Test the Keys ORM object."""

    obj_cls = Keys
    obj_id = Keys.id

    def test_keys_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_KEY_HASH)

    def test_unicode_keys_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_KEY_HASH)

    def test_keys_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_KEY_HASH))

    def test_key_search_expr(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_KEY_HASH,
            key_operator='ILIKE',
            key=u'%é%'
        )

    def test_keys_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_KEY_HASH)

    def test_unicode_keys_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_KEY_HASH)
