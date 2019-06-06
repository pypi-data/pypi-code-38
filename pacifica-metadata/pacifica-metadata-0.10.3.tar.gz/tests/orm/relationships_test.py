#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the relationships ORM object."""
from json import dumps
from pacifica.metadata.orm.relationships import Relationships
from .base_test import TestBase

SAMPLE_RELATIONSHIP_HASH = {
    'uuid': '2915294a-7014-44c3-9d94-8dd7b8ff34e8',
    'name': 'test_rel_1',
    'display_name': 'Test Relationship 1',
    'description': 'Some test relationship',
    'encoding': 'utf-8'
}

SAMPLE_UNICODE_RELATIONSHIP_HASH = {
    'uuid': 'cd4684e5-3d0f-4200-9549-ad74a6bdf399',
    'name': u'tést_rel_2',
    'display_name': u'Tést Relationship 2',
    'description': u'Some tést relationship with unicode',
    'encoding': 'utf-8'
}


class TestRelationships(TestBase):
    """Test the Relationships ORM object."""

    obj_cls = Relationships
    obj_id = Relationships.uuid

    def test_relationships_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_RELATIONSHIP_HASH)

    def test_unicode_relationships_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_RELATIONSHIP_HASH)

    def test_relationships_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_RELATIONSHIP_HASH))

    def test_relationships_search_expr(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_RELATIONSHIP_HASH,
            name_operator='ILIKE',
            name=u'%é%'
        )

    def test_relationships_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_RELATIONSHIP_HASH)

    def test_unicode_rel_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_RELATIONSHIP_HASH)
