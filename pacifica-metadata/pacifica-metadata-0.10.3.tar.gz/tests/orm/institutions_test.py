#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the keys ORM object."""
from json import dumps
from pacifica.metadata.orm.institutions import Institutions
from .base_test import TestBase

SAMPLE_INSTITUTION_HASH = {
    '_id': 127,
    'name': 'STFU',
    'association_cd': 'UNK',
    'is_foreign': True,
    'encoding': 'UTF8'
}

SAMPLE_UNICODE_INSTITUTION_HASH = {
    '_id': 127,
    'name': u'STFUé',
    'association_cd': 'UNK',
    'is_foreign': False,
    'encoding': 'UTF8'
}


class TestInstitutions(TestBase):
    """Test the Institutions ORM object."""

    obj_cls = Institutions
    obj_id = Institutions.id

    def test_institutions_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_INSTITUTION_HASH)

    def test_unicode_institutions_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_INSTITUTION_HASH)

    def test_institutions_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_INSTITUTION_HASH))

    def test_institutions_sexpr_uni(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_INSTITUTION_HASH,
            name_operator='ILIKE',
            name=u'%é%'
        )

    def test_institutions_sexpr_txt(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_INSTITUTION_HASH,
            name_operator='ILIKE',
            name='ST%'
        )

    def test_institutions_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_INSTITUTION_HASH)

    def test_unicode_institutions_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_INSTITUTION_HASH)
