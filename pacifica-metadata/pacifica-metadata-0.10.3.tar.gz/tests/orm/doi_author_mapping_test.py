#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the file_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.doi_author_mapping import DOIAuthorMapping
from pacifica.metadata.orm.doi_entries import DOIEntries
from pacifica.metadata.orm.doi_authors import DOIAuthors
from .base_test import TestBase
from .doi_entries_test import TestDOIEntries
from .doi_entries_test import SAMPLE_DOIENTRIES_HASH as SAMPLE_DOI_HASH
from .doi_entries_test import SAMPLE_UNICODE_DOIENTRIES_HASH as SAMPLE_UNICODE_DOI_HASH
from .doi_authors_test import TestDOIAuthors
from .doi_authors_test import SAMPLE_DOIAUTHORS_HASH as SAMPLE_AUTHOR_HASH
from .doi_authors_test import SAMPLE_UNICODE_DOIAUTHORS_HASH as SAMPLE_UNICODE_AUTHOR_HASH


SAMPLE_DOIAUTHORMAPPING_HASH = {
    'doi': SAMPLE_DOI_HASH['doi'],
    'author_order': 1,
    'author': SAMPLE_AUTHOR_HASH['_id']
}

# yes a DOI can be unicode....
# https://www.doi.org/doi_handbook/2_Numbering.html#2.2.1
SAMPLE_UNICODE_DOIAUTHORMAPPING_HASH = {
    'doi': SAMPLE_UNICODE_DOI_HASH['doi'],
    'author_order': 1,
    'author': SAMPLE_UNICODE_AUTHOR_HASH['_id']
}


class TestDOIAuthorMapping(TestBase):
    """Test the DOIAuthorMapping ORM object."""

    obj_cls = DOIAuthorMapping
    obj_id = DOIAuthorMapping.doi

    @classmethod
    def base_create_dep_objs(cls):
        """Make dependent DOI entry and DOI Author objects."""
        doi = DOIEntries()
        TestDOIEntries.base_create_dep_objs()
        doi.from_hash(SAMPLE_DOI_HASH)
        doi.save(force_insert=True)

        uni_doi = DOIEntries()
        uni_doi.from_hash(SAMPLE_UNICODE_DOI_HASH)
        uni_doi.save(force_insert=True)

        author = DOIAuthors()
        TestDOIAuthors.base_create_dep_objs()
        author.from_hash(SAMPLE_AUTHOR_HASH)
        author.save(force_insert=True)

        uni_author = DOIAuthors()
        uni_author.from_hash(SAMPLE_UNICODE_AUTHOR_HASH)
        uni_author.save(force_insert=True)

    def test_doi_author_mapping_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_DOIAUTHORMAPPING_HASH)

    def test_uc_doi_author_mapping_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_DOIAUTHORMAPPING_HASH)

    def test_doi_author_mapping_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_DOIAUTHORMAPPING_HASH))

    def test_doi_author_mapping_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_DOIAUTHORMAPPING_HASH)

    def test_uc_doi_authormapping_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_DOIAUTHORMAPPING_HASH)
