#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the file_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.institution_user import InstitutionUser
from pacifica.metadata.orm.institutions import Institutions
from pacifica.metadata.orm.relationships import Relationships
from pacifica.metadata.orm.users import Users
from .base_test import TestBase
from .institutions_test import SAMPLE_INSTITUTION_HASH, TestInstitutions
from .users_test import SAMPLE_USER_HASH, TestUsers
from .relationships_test import SAMPLE_RELATIONSHIP_HASH, TestRelationships

SAMPLE_INSTITUTION_USER_HASH = {
    'uuid': '0e921e85-ef20-47b3-91e1-fb9adc26f65a',
    'user': SAMPLE_USER_HASH['_id'],
    'relationship': SAMPLE_RELATIONSHIP_HASH['uuid'],
    'institution': SAMPLE_INSTITUTION_HASH['_id']
}


class TestInstitutionUser(TestBase):
    """Test the InstitutionUser ORM object."""

    obj_cls = InstitutionUser
    obj_id = InstitutionUser.user

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that InstitutionUser need."""
        rel = Relationships()
        TestRelationships.base_create_dep_objs()
        rel.from_hash(SAMPLE_RELATIONSHIP_HASH)
        rel.save(force_insert=True)
        inst = Institutions()
        TestInstitutions.base_create_dep_objs()
        inst.from_hash(SAMPLE_INSTITUTION_HASH)
        inst.save(force_insert=True)
        user1 = Users()
        TestUsers.base_create_dep_objs()
        user1.from_hash(SAMPLE_USER_HASH)
        user1.save(force_insert=True)

    def test_institution_user_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_INSTITUTION_USER_HASH)

    def test_institution_user_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_INSTITUTION_USER_HASH))

    def test_institution_user_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_INSTITUTION_USER_HASH)
