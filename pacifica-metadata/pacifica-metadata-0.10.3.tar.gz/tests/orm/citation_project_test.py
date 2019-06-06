#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the file_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.citation_project import CitationProject
from pacifica.metadata.orm.projects import Projects
from pacifica.metadata.orm.citations import Citations
from .base_test import TestBase
from .projects_test import SAMPLE_PROJECT_HASH, TestProjects
from .citations_test import SAMPLE_CITATION_HASH, TestCitations

SAMPLE_CITATION_PROJECT_HASH = {
    'project': SAMPLE_PROJECT_HASH['_id'],
    'citation': SAMPLE_CITATION_HASH['_id']
}


class TestCitationProject(TestBase):
    """Test the InstitutionPerson ORM object."""

    obj_cls = CitationProject
    obj_id = CitationProject.project

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that FileKeyValue need."""
        proj1 = Projects()
        TestProjects.base_create_dep_objs()
        proj1.from_hash(SAMPLE_PROJECT_HASH)
        proj1.save(force_insert=True)
        cite = Citations()
        TestCitations.base_create_dep_objs()
        cite.from_hash(SAMPLE_CITATION_HASH)
        cite.save(force_insert=True)

    def test_citation_project_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_CITATION_PROJECT_HASH)

    def test_citation_project_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_CITATION_PROJECT_HASH))

    def test_citation_project_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_CITATION_PROJECT_HASH)
