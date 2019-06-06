#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the project_group ORM object."""
from json import dumps
from pacifica.metadata.orm.project_group import ProjectGroup
from pacifica.metadata.orm.groups import Groups
from pacifica.metadata.orm.projects import Projects
from .base_test import TestBase
from .groups_test import SAMPLE_GROUP_HASH, TestGroups
from .projects_test import SAMPLE_PROJECT_HASH, TestProjects

SAMPLE_PROJECT_GROUP_HASH = {
    'project': SAMPLE_PROJECT_HASH['_id'],
    'group': SAMPLE_GROUP_HASH['_id']
}


class TestProjectGroup(TestBase):
    """Test the ProjectGroup ORM object."""

    obj_cls = ProjectGroup
    obj_id = ProjectGroup.project

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that ProjectGroup need."""
        grp = Groups()
        TestGroups.base_create_dep_objs()
        grp.from_hash(SAMPLE_GROUP_HASH)
        grp.save(force_insert=True)
        proj2 = Projects()
        TestProjects.base_create_dep_objs()
        proj2.from_hash(SAMPLE_PROJECT_HASH)
        proj2.save(force_insert=True)

    def test_project_group_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_PROJECT_GROUP_HASH)

    def test_project_group_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_PROJECT_GROUP_HASH))

    def test_project_group_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_PROJECT_GROUP_HASH)
