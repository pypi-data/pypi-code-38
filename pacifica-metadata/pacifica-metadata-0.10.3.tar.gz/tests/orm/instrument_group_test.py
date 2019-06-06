#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the user_group ORM object."""
from json import dumps
from pacifica.metadata.orm.instrument_group import InstrumentGroup
from pacifica.metadata.orm.instruments import Instruments
from pacifica.metadata.orm.groups import Groups
from .base_test import TestBase
from .instruments_test import SAMPLE_INSTRUMENT_HASH, TestInstruments
from .groups_test import SAMPLE_GROUP_HASH, TestGroups

SAMPLE_INSTRUMENT_GROUP_HASH = {
    'instrument': SAMPLE_INSTRUMENT_HASH['_id'],
    'group': SAMPLE_GROUP_HASH['_id']
}


class TestInstrumentGroup(TestBase):
    """Test the Keys ORM object."""

    obj_cls = InstrumentGroup
    obj_id = InstrumentGroup.instrument

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that InstrumentGroup need."""
        groups = Groups()
        TestGroups.base_create_dep_objs()
        groups.from_hash(SAMPLE_GROUP_HASH)
        groups.save(force_insert=True)
        inst = Instruments()
        TestInstruments.base_create_dep_objs()
        inst.from_hash(SAMPLE_INSTRUMENT_HASH)
        inst.save(force_insert=True)

    def test_instrument_group_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_INSTRUMENT_GROUP_HASH)

    def test_instrument_group_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_INSTRUMENT_GROUP_HASH))

    def test_instrument_group_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_INSTRUMENT_GROUP_HASH)
