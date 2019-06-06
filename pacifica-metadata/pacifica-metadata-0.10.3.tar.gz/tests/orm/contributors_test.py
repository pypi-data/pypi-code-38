#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the contributors ORM object."""
from json import dumps
from pacifica.metadata.orm.contributors import Contributors
from pacifica.metadata.orm.users import Users
from pacifica.metadata.orm.institutions import Institutions
from .base_test import TestBase
from .users_test import SAMPLE_USER_HASH, TestUsers
from .institutions_test import SAMPLE_INSTITUTION_HASH, TestInstitutions

SAMPLE_CONTRIBUTOR_HASH = {
    '_id': 192,
    'user': SAMPLE_USER_HASH['_id'],
    'first_name': 'John',
    'middle_initial': 'F',
    'last_name': 'Doe',
    'dept_code': 'Ecology',
    'institution': SAMPLE_INSTITUTION_HASH['_id']
}

SAMPLE_UNICODE_CONTRIBUTOR_HASH = {
    '_id': 195,
    'user': SAMPLE_USER_HASH['_id'],
    'first_name': u'Jéhn',
    'middle_initial': u'Fé',
    'last_name': u'Doé',
    'dept_code': u'Ecologéy',
    'institution': SAMPLE_INSTITUTION_HASH['_id'],
    'encoding': 'UTF8'
}


class TestContributors(TestBase):
    """Test the Institutions ORM object."""

    obj_cls = Contributors
    obj_id = Contributors.id

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that Files depend on."""
        user = Users()
        TestUsers.base_create_dep_objs()
        user.from_hash(SAMPLE_USER_HASH)
        user.save(force_insert=True)
        inst = Institutions()
        TestInstitutions.base_create_dep_objs()
        inst.from_hash(SAMPLE_INSTITUTION_HASH)
        inst.save(force_insert=True)

    def test_contributors_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_CONTRIBUTOR_HASH)

    def test_unicode_contributors_hash(self):
        """Test the unicode hash using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_CONTRIBUTOR_HASH)

    def test_contributors_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_CONTRIBUTOR_HASH))

    def test_contributors_sexpr_uni(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_CONTRIBUTOR_HASH,
            first_name_operator='ILIKE',
            first_name=u'%é%'
        )

    def test_contributors_sexpr_txt(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_CONTRIBUTOR_HASH,
            last_name_operator='ILIKE',
            last_name='Do%'
        )

    def test_contributors_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_CONTRIBUTOR_HASH)

    def test_unicode_contributors_where(self):
        """Test the unicode hash using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_CONTRIBUTOR_HASH)
