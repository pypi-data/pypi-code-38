#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the keys ORM object."""
from json import dumps
from pacifica.metadata.orm.values import Values
from .base_test import TestBase

SAMPLE_VALUE_HASH = {
    '_id': 127,
    'value': '43278a',
    'display_name': '43278a',
    'description': '43278a',
    'encoding': 'UTF8'
}

SAMPLE_UNICODE_VALUE_HASH = {
    '_id': 127,
    'value': u'43278é',
    'display_name': u'43278é',
    'description': u'43278é',
    'encoding': 'UTF8'
}


class TestValues(TestBase):
    """Test the Values ORM object."""

    obj_cls = Values
    obj_id = Values.id

    def test_values_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_VALUE_HASH)

    def test_unicode_values_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_VALUE_HASH)

    def test_values_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_VALUE_HASH))

    def test_key_search_expr(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_VALUE_HASH,
            value_operator='ILIKE',
            value=u'%é%'
        )

    def test_values_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_VALUE_HASH)

    def test_unicode_values_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_VALUE_HASH)
