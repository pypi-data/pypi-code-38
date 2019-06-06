#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the projects ORM object."""
from datetime import datetime
from json import dumps
from pacifica.metadata.orm.utils import datetime_now_nomicrosecond
from pacifica.metadata.orm.projects import Projects
from .base_test import TestBase

SAMPLE_PROJECT_HASH = {
    '_id': '17a',
    'title': 'My Project Title',
    'short_name': 'Short Name for Display',
    'abstract': """
This is my project that's really cool and you should accept it. ;)
""",
    'science_theme': 'Nobel Prize Winners',
    'project_type': 'Blarg!',
    'encoding': 'UTF8',
    'submitted_date': datetime_now_nomicrosecond().isoformat(),
    'accepted_date': datetime.utcnow().date().isoformat(),
    'actual_start_date': datetime.utcnow().date().isoformat(),
    'actual_end_date': datetime.utcnow().date().isoformat(),
    'closed_date': datetime.utcnow().date().isoformat(),
    'suspense_date': datetime.utcnow().date().isoformat()
}

SAMPLE_UNICODE_PROJECT_HASH = {
    '_id': u'17é',
    'title': u'My Project Titlé',
    'short_name': u'Short Namé for Display',
    'abstract': u"""
This is my project that's réally cool and you should accept it. ;)
""",
    'science_theme': u'Nobél Prize Winners',
    'project_type': u'Blarg!é',
    'encoding': 'UTF8',
    'submitted_date': datetime_now_nomicrosecond().isoformat(),
    'accepted_date': datetime.utcnow().date().isoformat(),
    'actual_start_date': datetime.utcnow().date().isoformat(),
    'actual_end_date': datetime.utcnow().date().isoformat(),
    'closed_date': datetime.utcnow().date().isoformat(),
    'suspense_date': datetime.utcnow().date().isoformat()
}


class TestProjects(TestBase):
    """Test the Projects ORM object."""

    obj_cls = Projects
    obj_id = Projects.id

    def test_projects_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_PROJECT_HASH)

    def test_unicode_projects_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_PROJECT_HASH)

    def test_projects_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_PROJECT_HASH))

    def test_projects_sexpr_uni(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_PROJECT_HASH,
            title_operator='ILIKE',
            title=u'%é%'
        )

    def test_projects_sexpr_txt(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_PROJECT_HASH,
            abstract_operator='ILIKE',
            abstract='%This%'
        )

    def test_projects_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_PROJECT_HASH)

    def test_unicode_projects_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_PROJECT_HASH)
