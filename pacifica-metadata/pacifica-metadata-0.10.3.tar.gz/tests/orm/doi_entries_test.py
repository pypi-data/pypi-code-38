#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the file_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.doi_entries import DOIEntries
from pacifica.metadata.orm.users import Users
from .base_test import TestBase
from .users_test import SAMPLE_USER_HASH as SAMPLE_CREATOR_HASH
from .users_test import SAMPLE_UNICODE_USER_HASH as SAMPLE_UNICODE_CREATOR_HASH
from .users_test import TestUsers

SAMPLE_DOIENTRIES_HASH = {
    'doi': u'10.25584/data.2018-03.127/1234567',
    'status': 'completed',
    'site_url': 'https://release.datahub.pnnl.gov/released_data/127',
    'encoding': 'UTF8',
    'creator': SAMPLE_CREATOR_HASH['_id']
}

# yes a DOI can be unicode....
# https://www.doi.org/doi_handbook/2_Numbering.html#2.2.1
SAMPLE_UNICODE_DOIENTRIES_HASH = {
    'doi': u'10.25584/data.café.2018-03.127/1234568',
    'status': 'completed',
    'site_url': 'https://release.datahub.pnnl.gov/released_data/127',
    'encoding': 'UTF8',
    'creator': SAMPLE_UNICODE_CREATOR_HASH['_id']
}


class TestDOIEntries(TestBase):
    """Test the DOIEntries ORM object."""

    obj_cls = DOIEntries
    obj_id = DOIEntries.doi

    @classmethod
    def base_create_dep_objs(cls):
        """Build the object and make dependent user object."""
        submitter = Users()
        TestUsers.base_create_dep_objs()
        submitter.from_hash(SAMPLE_CREATOR_HASH)
        submitter.save(force_insert=True)

        uni_submitter = Users()
        uni_submitter.from_hash(SAMPLE_UNICODE_CREATOR_HASH)
        uni_submitter.save(force_insert=True)

    def test_doientries_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_DOIENTRIES_HASH)

    def test_unicode_doientries_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_DOIENTRIES_HASH)

    def test_doientries_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_DOIENTRIES_HASH))

    def test_doientries_search_expr(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_DOIENTRIES_HASH,
            keyword_operator='ILIKE',
            keyword=u'%é%'
        )

    def test_doientries_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_DOIENTRIES_HASH)

    def test_unicode_doientries_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_DOIENTRIES_HASH)
