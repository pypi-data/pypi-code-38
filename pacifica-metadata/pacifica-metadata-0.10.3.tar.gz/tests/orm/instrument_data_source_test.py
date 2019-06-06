#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the user_group ORM object."""
from json import dumps
from pacifica.metadata.orm.instrument_data_source import InstrumentDataSource
from pacifica.metadata.orm.instruments import Instruments
from pacifica.metadata.orm.data_sources import DataSources
from pacifica.metadata.orm.relationships import Relationships
from .base_test import TestBase
from .instruments_test import SAMPLE_INSTRUMENT_HASH, TestInstruments
from .data_sources_test import SAMPLE_DATA_SOURCE_HASH, TestDataSources
from .relationships_test import SAMPLE_RELATIONSHIP_HASH, TestRelationships

SAMPLE_INSTRUMENT_DATA_SOURCE_HASH = {
    'instrument': SAMPLE_INSTRUMENT_HASH['_id'],
    'data_source': SAMPLE_DATA_SOURCE_HASH['uuid'],
    'relationship': SAMPLE_RELATIONSHIP_HASH['uuid']
}


class TestInstrumentDataSource(TestBase):
    """Test the Keys ORM object."""

    obj_cls = InstrumentDataSource
    obj_id = InstrumentDataSource.instrument

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that InstrumentGroup need."""
        data_source = DataSources()
        TestDataSources.base_create_dep_objs()
        data_source.from_hash(SAMPLE_DATA_SOURCE_HASH)
        data_source.save(force_insert=True)
        inst = Instruments()
        TestInstruments.base_create_dep_objs()
        inst.from_hash(SAMPLE_INSTRUMENT_HASH)
        inst.save(force_insert=True)
        rel = Relationships()
        TestRelationships.base_create_dep_objs()
        rel.from_hash(SAMPLE_RELATIONSHIP_HASH)
        rel.save(force_insert=True)

    def test_inst_data_source_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_INSTRUMENT_DATA_SOURCE_HASH)

    def test_inst_data_source_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_INSTRUMENT_DATA_SOURCE_HASH))

    def test_inst_data_source_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_INSTRUMENT_DATA_SOURCE_HASH)
