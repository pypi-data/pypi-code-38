#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the analytical tools ORM object."""
from json import dumps
from pacifica.metadata.orm.analytical_tools import AnalyticalTools
from .base_test import TestBase

SAMPLE_TOOL_HASH = {
    '_id': 127,
    'name': 'My Custom Code',
    'encoding': 'UTF8'
}

SAMPLE_UNICODE_TOOL_HASH = {
    '_id': 127,
    'name': u'My Cutstom Codé',
    'encoding': 'UTF8'
}


class TestAnalyticalTools(TestBase):
    """Test the AnalyticalTools ORM object."""

    obj_cls = AnalyticalTools
    obj_id = AnalyticalTools.id

    def test_tools_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_TOOL_HASH)

    def test_unicode_tools_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_TOOL_HASH)

    def test_tools_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_TOOL_HASH))

    def test_tools_where_search_expr(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_TOOL_HASH, name_operator='ILIKE', name='%Custom%')

    def test_tools_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_TOOL_HASH)

    def test_unicode_tools_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_TOOL_HASH)
