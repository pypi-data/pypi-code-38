#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the file_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.doi_authors import DOIAuthors
from .base_test import TestBase
from .users_test import SAMPLE_USER_HASH, SAMPLE_UNICODE_USER_HASH

SAMPLE_DOIAUTHORS_HASH = {
    '_id': 1,
    'last_name': SAMPLE_USER_HASH['last_name'],
    'first_name': SAMPLE_USER_HASH['first_name'],
    'email': SAMPLE_USER_HASH['email_address'],
    'affiliation': 'EMSL',
    'orcid': '1234-2345-3456-4567'
}

# yes a DOI can be unicode....
# https://www.doi.org/doi_handbook/2_Numbering.html#2.2.1
SAMPLE_UNICODE_DOIAUTHORS_HASH = {
    '_id': 2,
    'last_name': SAMPLE_UNICODE_USER_HASH['last_name'],
    'first_name': SAMPLE_UNICODE_USER_HASH['first_name'],
    'email': SAMPLE_UNICODE_USER_HASH['email_address'],
    'affiliation': 'EMSL',
    'orcid': '1234-2345-3456-4567'
}


class TestDOIAuthors(TestBase):
    """Test the DOIAuthors ORM object."""

    obj_cls = DOIAuthors
    obj_id = DOIAuthors.id

    def test_doiauthors_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_DOIAUTHORS_HASH)

    def test_unicode_doiauthors_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_DOIAUTHORS_HASH)

    def test_doiauthors_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_DOIAUTHORS_HASH))

    def test_doiauthors_search_expr(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_DOIAUTHORS_HASH,
            keyword_operator='ILIKE',
            keyword=u'%é%'
        )

    def test_doiauthors_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_DOIAUTHORS_HASH)

    def test_unicode_doiauthors_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_DOIAUTHORS_HASH)
