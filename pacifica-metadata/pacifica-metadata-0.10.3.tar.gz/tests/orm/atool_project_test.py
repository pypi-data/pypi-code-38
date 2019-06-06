#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the atool_project ORM object."""
from json import dumps
from pacifica.metadata.orm.atool_project import AToolProject
from pacifica.metadata.orm.projects import Projects
from pacifica.metadata.orm.analytical_tools import AnalyticalTools
from .base_test import TestBase
from .projects_test import SAMPLE_PROJECT_HASH, TestProjects
from .analytical_tools_test import SAMPLE_TOOL_HASH, TestAnalyticalTools

SAMPLE_TOOL_PROJECT_HASH = {
    'project': SAMPLE_PROJECT_HASH['_id'],
    'analytical_tool': SAMPLE_TOOL_HASH['_id']
}


class TestAToolProject(TestBase):
    """Test the Keys ORM object."""

    obj_cls = AToolProject
    obj_id = AToolProject.project

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that TransactionKeyValue need."""
        proj = Projects()
        tool = AnalyticalTools()
        TestProjects.base_create_dep_objs()
        proj.from_hash(SAMPLE_PROJECT_HASH)
        proj.save(force_insert=True)
        TestAnalyticalTools.base_create_dep_objs()
        tool.from_hash(SAMPLE_TOOL_HASH)
        tool.save(force_insert=True)

    def test_tool_proj_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_TOOL_PROJECT_HASH)

    def test_tool_proj_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_TOOL_PROJECT_HASH))

    def test_tool_proj_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_TOOL_PROJECT_HASH)
