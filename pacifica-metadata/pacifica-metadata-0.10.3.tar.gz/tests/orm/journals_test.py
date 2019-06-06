#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the journals ORM object."""
from json import dumps
from pacifica.metadata.orm.journals import Journals
from .base_test import TestBase

SAMPLE_JOURNAL_HASH = {
    '_id': 45,
    'name': 'Northern Yukon Master Workworking',
    'impact_factor': 10.0,
    'website_url': 'http://www.ehwoodworkers.ca'
}

SAMPLE_UNICODE_JOURNAL_HASH = {
    '_id': 45,
    'name': u'Northern Yukon Mastér Workworking',
    'impact_factor': 10.0,
    'website_url': 'http://www.ehwoodworkers.ca',
    'encoding': 'UTF-8'
}


class TestJournals(TestBase):
    """Test the Journals ORM object."""

    obj_cls = Journals
    obj_id = Journals.id

    def test_journal_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_JOURNAL_HASH)

    def test_unicode_journal_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_JOURNAL_HASH)

    def test_journal_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_JOURNAL_HASH))

    def test_journals_sexpr_ilike(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_JOURNAL_HASH,
            name_operator='ILIKE',
            name=u'%é%'
        )

    def test_journals_sexpr_gt(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_JOURNAL_HASH,
            impact_factor_operator='GT',
            impact_factor=9.5
        )

    def test_journal_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_JOURNAL_HASH)

    def test_unicode_journal_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_JOURNAL_HASH)
