#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the user_group ORM object."""
from json import dumps
from pacifica.metadata.orm.user_group import UserGroup
from pacifica.metadata.orm.users import Users
from pacifica.metadata.orm.groups import Groups
from .base_test import TestBase
from .users_test import SAMPLE_USER_HASH, TestUsers
from .groups_test import SAMPLE_GROUP_HASH, TestGroups

SAMPLE_USER_GROUP_HASH = {
    'person': SAMPLE_USER_HASH['_id'],
    'group': SAMPLE_GROUP_HASH['_id']
}


class TestUserGroup(TestBase):
    """Test the Keys ORM object."""

    obj_cls = UserGroup
    obj_id = UserGroup.person

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that UserGroup need."""
        member = Users()
        TestUsers.base_create_dep_objs()
        member.from_hash(SAMPLE_USER_HASH)
        member.save(force_insert=True)
        groups = Groups()
        TestGroups.base_create_dep_objs()
        groups.from_hash(SAMPLE_GROUP_HASH)
        groups.save(force_insert=True)

    def test_user_group_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_USER_GROUP_HASH)

    def test_user_group_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_USER_GROUP_HASH))

    def test_user_group_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_USER_GROUP_HASH)
