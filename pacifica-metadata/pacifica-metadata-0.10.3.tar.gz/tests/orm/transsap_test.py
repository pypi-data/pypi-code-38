#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the keys ORM object."""
from json import dumps
from pacifica.metadata.orm.transsap import TransSAP
from pacifica.metadata.orm.transactions import Transactions
from pacifica.metadata.orm.users import Users
from pacifica.metadata.orm.projects import Projects
from pacifica.metadata.orm.analytical_tools import AnalyticalTools
from .base_test import TestBase
from .transactions_test import SAMPLE_TRANSACTION_HASH, TestTransactions
from .users_test import SAMPLE_USER_HASH as SAMPLE_SUBMITTER_HASH, TestUsers
from .projects_test import SAMPLE_PROJECT_HASH, TestProjects
from .analytical_tools_test import SAMPLE_TOOL_HASH, TestAnalyticalTools

SAMPLE_TRANSSAP_HASH = {
    '_id': SAMPLE_TRANSACTION_HASH['_id'],
    'submitter': SAMPLE_SUBMITTER_HASH['_id'],
    'project': SAMPLE_PROJECT_HASH['_id'],
    'analytical_tool': SAMPLE_TOOL_HASH['_id']
}


class TestTransSAP(TestBase):
    """Test the Transactions ORM object."""

    obj_cls = TransSAP
    obj_id = TransSAP.id

    @classmethod
    def base_create_dep_objs(cls):
        """Build the object and make dependent user object."""
        proj = Projects()
        TestProjects.base_create_dep_objs()
        proj.from_hash(SAMPLE_PROJECT_HASH)
        proj.save(force_insert=True)
        submitter = Users()
        TestUsers.base_create_dep_objs()
        submitter.from_hash(SAMPLE_SUBMITTER_HASH)
        submitter.save(force_insert=True)
        atool = AnalyticalTools()
        TestAnalyticalTools.base_create_dep_objs()
        atool.from_hash(SAMPLE_TOOL_HASH)
        atool.save(force_insert=True)
        trans = Transactions()
        TestTransactions.base_create_dep_objs()
        trans.from_hash(SAMPLE_TRANSACTION_HASH)
        trans.save(force_insert=True)

    def test_transsap_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_TRANSSAP_HASH)

    def test_transsap_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_TRANSSAP_HASH))

    def test_transsap_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_TRANSSAP_HASH)
