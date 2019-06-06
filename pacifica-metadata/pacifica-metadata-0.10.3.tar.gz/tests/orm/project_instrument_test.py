#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the project_instrument ORM object."""
from json import dumps
from pacifica.metadata.orm.project_instrument import ProjectInstrument
from pacifica.metadata.orm.instruments import Instruments
from pacifica.metadata.orm.relationships import Relationships
from pacifica.metadata.orm.projects import Projects
from .base_test import TestBase
from .instruments_test import SAMPLE_INSTRUMENT_HASH, TestInstruments
from .projects_test import SAMPLE_PROJECT_HASH, TestProjects
from .relationships_test import SAMPLE_RELATIONSHIP_HASH, TestRelationships

SAMPLE_PROJECT_INSTRUMENT_HASH = {
    'uuid': 'e22d18c3-b3ee-4265-b34f-389af6a7f39c',
    'project': SAMPLE_PROJECT_HASH['_id'],
    'relationship': SAMPLE_RELATIONSHIP_HASH['uuid'],
    'instrument': SAMPLE_INSTRUMENT_HASH['_id']
}


class TestProjectInstrument(TestBase):
    """Test the ProjectInstrument ORM object."""

    obj_cls = ProjectInstrument
    obj_id = ProjectInstrument.project

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that FileKeyValue need."""
        rel = Relationships()
        TestRelationships.base_create_dep_objs()
        rel.from_hash(SAMPLE_RELATIONSHIP_HASH)
        rel.save(force_insert=True)
        proj2 = Projects()
        TestProjects.base_create_dep_objs()
        proj2.from_hash(SAMPLE_PROJECT_HASH)
        proj2.save(force_insert=True)
        inst = Instruments()
        TestInstruments.base_create_dep_objs()
        inst.from_hash(SAMPLE_INSTRUMENT_HASH)
        inst.save(force_insert=True)

    def test_project_instrument_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_PROJECT_INSTRUMENT_HASH)

    def test_project_instrument_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_PROJECT_INSTRUMENT_HASH))

    def test_project_instrument_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_PROJECT_INSTRUMENT_HASH)
