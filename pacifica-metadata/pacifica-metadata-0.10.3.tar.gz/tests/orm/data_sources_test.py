#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the data_sources ORM object."""
from json import dumps
from pacifica.metadata.orm.data_sources import DataSources
from .base_test import TestBase

SAMPLE_DATA_SOURCE_HASH = {
    'uuid': '35326981-b461-431e-b3e1-dc044ffb4b8d',
    'name': 'test_rel_1',
    'uri': 'cifs://user:password@fs.example.com/some_share/some_dir',
    'display_name': 'Test Data Source 1',
    'description': 'Some test data source',
    'encoding': 'utf-8'
}

SAMPLE_UNICODE_DATA_SOURCE_HASH = {
    'uuid': 'b5929256-7063-47ca-aac3-91ed216c8c60',
    'name': u'tést_rel_2',
    'uri': 'cifs://user:password@fs.example.com/some_share/some_dir',
    'display_name': u'Tést Data Source 2',
    'description': u'Some tést data source with unicode',
    'encoding': 'utf-8'
}


class TestDataSources(TestBase):
    """Test the DataSources ORM object."""

    obj_cls = DataSources
    obj_id = DataSources.uuid

    def test_data_sources_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_DATA_SOURCE_HASH)

    def test_unicode_data_sources_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_DATA_SOURCE_HASH)

    def test_data_sources_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_DATA_SOURCE_HASH))

    def test_data_sources_search_expr(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_DATA_SOURCE_HASH,
            name_operator='ILIKE',
            name=u'%é%'
        )

    def test_data_sources_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_DATA_SOURCE_HASH)

    def test_unicode_data_sources_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_DATA_SOURCE_HASH)
