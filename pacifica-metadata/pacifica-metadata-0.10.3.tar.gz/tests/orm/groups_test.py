#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the groups ORM object."""
from json import dumps
from pacifica.metadata.orm.groups import Groups
from .base_test import TestBase

SAMPLE_GROUP_HASH = {
    '_id': 10,
    'name': 'custodians',
    'display_name': 'Custodians',
    'description': 'Members of this group are responsible for something.',
    'is_admin': True,
    'encoding': 'UTF8'
}

SAMPLE_UNICODE_GROUP_HASH = {
    '_id': 11,
    'name': u'Bléh',
    'display_name': u'Bléh',
    'description': u'Bléh',
    'is_admin': False,
    'encoding': 'UTF8'
}


class TestGroups(TestBase):
    """Test the Groups ORM object."""

    obj_cls = Groups
    obj_id = Groups.id

    def test_group_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_GROUP_HASH)

    def test_unicode_group_hash(self):
        """Test the unicode hash using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_GROUP_HASH)

    def test_group_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_GROUP_HASH))

    def test_group_search_expr(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_GROUP_HASH,
            name_operator='ILIKE',
            name=u'%é%'
        )

    def test_group_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_GROUP_HASH)

    def test_unicode_group_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_GROUP_HASH)
