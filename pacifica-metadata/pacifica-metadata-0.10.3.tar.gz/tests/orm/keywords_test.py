#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the file_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.keywords import Keywords
from .base_test import TestBase

SAMPLE_KEYWORD_HASH = {
    '_id': 142,
    'keyword': 'halitosis',
    'encoding': 'UTF8'
}

SAMPLE_UNICODE_KEYWORD_HASH = {
    '_id': 143,
    'keyword': u'blargééééé',
    'encoding': 'UTF8'
}


class TestKeywords(TestBase):
    """Test the Keywords ORM object."""

    obj_cls = Keywords
    obj_id = Keywords.id

    def test_keywords_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_KEYWORD_HASH)

    def test_unicode_keywords_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_KEYWORD_HASH)

    def test_keywords_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_KEYWORD_HASH))

    def test_keywords_search_expr(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_KEYWORD_HASH,
            keyword_operator='ILIKE',
            keyword=u'%é%'
        )

    def test_keywords_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_KEYWORD_HASH)

    def test_unicode_keywords_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_KEYWORD_HASH)
