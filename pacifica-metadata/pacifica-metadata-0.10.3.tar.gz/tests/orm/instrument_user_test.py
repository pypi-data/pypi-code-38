#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the file_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.instrument_user import InstrumentUser
from pacifica.metadata.orm.instruments import Instruments
from pacifica.metadata.orm.users import Users
from pacifica.metadata.orm.relationships import Relationships
from .base_test import TestBase
from .instruments_test import SAMPLE_INSTRUMENT_HASH, TestInstruments
from .users_test import SAMPLE_USER_HASH, TestUsers
from .relationships_test import SAMPLE_RELATIONSHIP_HASH, TestRelationships

SAMPLE_INSTRUMENT_USER_HASH = {
    'uuid': 'a52abbe0-b3ec-40b8-83c5-65ebcd857b00',
    'user': SAMPLE_USER_HASH['_id'],
    'relationship': SAMPLE_RELATIONSHIP_HASH['uuid'],
    'instrument': SAMPLE_INSTRUMENT_HASH['_id']
}


class TestInstrumentUser(TestBase):
    """Test the InstitutionPerson ORM object."""

    obj_cls = InstrumentUser
    obj_id = InstrumentUser.user

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that InstrumentUser need."""
        rel = Relationships()
        TestRelationships.base_create_dep_objs()
        rel.from_hash(SAMPLE_RELATIONSHIP_HASH)
        rel.save(force_insert=True)
        inst = Instruments()
        TestInstruments.base_create_dep_objs()
        inst.from_hash(SAMPLE_INSTRUMENT_HASH)
        inst.save(force_insert=True)
        user1 = Users()
        TestUsers.base_create_dep_objs()
        user1.from_hash(SAMPLE_USER_HASH)
        user1.save(force_insert=True)

    def test_instrument_user_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_INSTRUMENT_USER_HASH)

    def test_instrument_user_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_INSTRUMENT_USER_HASH))

    def test_instrument_user_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_INSTRUMENT_USER_HASH)
