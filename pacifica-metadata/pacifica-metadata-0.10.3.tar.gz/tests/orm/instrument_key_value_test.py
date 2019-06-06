#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the instrument_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.instrument_key_value import InstrumentKeyValue
from pacifica.metadata.orm.instruments import Instruments
from pacifica.metadata.orm.relationships import Relationships
from pacifica.metadata.orm.keys import Keys
from pacifica.metadata.orm.values import Values
from .base_test import TestBase
from .instruments_test import SAMPLE_INSTRUMENT_HASH, TestInstruments
from .relationships_test import SAMPLE_RELATIONSHIP_HASH, TestRelationships
from .keys_test import SAMPLE_KEY_HASH, TestKeys
from .values_test import SAMPLE_VALUE_HASH, TestValues

SAMPLE_INSTRUMENT_KEY_VALUE_HASH = {
    'instrument': SAMPLE_INSTRUMENT_HASH['_id'],
    'key': SAMPLE_KEY_HASH['_id'],
    'value': SAMPLE_VALUE_HASH['_id'],
    'relationship': SAMPLE_RELATIONSHIP_HASH['uuid']
}


class TestInstrumentKeyValue(TestBase):
    """Test the Keys ORM object."""

    obj_cls = InstrumentKeyValue
    obj_id = InstrumentKeyValue.instrument

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that InstrumentKeyValue need."""
        rel = Relationships()
        inst = Instruments()
        keys = Keys()
        values = Values()
        TestRelationships.base_create_dep_objs()
        rel.from_hash(SAMPLE_RELATIONSHIP_HASH)
        rel.save(force_insert=True)
        TestInstruments.base_create_dep_objs()
        inst.from_hash(SAMPLE_INSTRUMENT_HASH)
        inst.save(force_insert=True)
        TestKeys.base_create_dep_objs()
        keys.from_hash(SAMPLE_KEY_HASH)
        keys.save(force_insert=True)
        TestValues.base_create_dep_objs()
        values.from_hash(SAMPLE_VALUE_HASH)
        values.save(force_insert=True)

    def test_instrument_key_value_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_INSTRUMENT_KEY_VALUE_HASH)

    def test_instrument_key_value_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_INSTRUMENT_KEY_VALUE_HASH))

    def test_instrument_key_value_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_INSTRUMENT_KEY_VALUE_HASH)
