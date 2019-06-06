#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the keys ORM object."""
from json import dumps
from pacifica.metadata.orm.transsip import TransSIP
from pacifica.metadata.orm.transactions import Transactions
from pacifica.metadata.orm.users import Users
from pacifica.metadata.orm.projects import Projects
from pacifica.metadata.orm.instruments import Instruments
from .base_test import TestBase
from .transactions_test import SAMPLE_TRANSACTION_HASH, TestTransactions
from .users_test import SAMPLE_USER_HASH as SAMPLE_SUBMITTER_HASH, TestUsers
from .projects_test import SAMPLE_PROJECT_HASH, TestProjects
from .instruments_test import SAMPLE_INSTRUMENT_HASH, TestInstruments

SAMPLE_TRANSSIP_HASH = {
    '_id': SAMPLE_TRANSACTION_HASH['_id'],
    'submitter': SAMPLE_SUBMITTER_HASH['_id'],
    'project': SAMPLE_PROJECT_HASH['_id'],
    'instrument': SAMPLE_INSTRUMENT_HASH['_id']
}


class TestTransSIP(TestBase):
    """Test the Transactions ORM object."""

    obj_cls = TransSIP
    obj_id = TransSIP.id

    @classmethod
    def base_create_dep_objs(cls):
        """Build the object and make dependent user object."""
        submitter, _created = Users().get_or_create(
            id=SAMPLE_SUBMITTER_HASH['_id'])
        TestUsers.base_create_dep_objs()
        submitter.from_hash(SAMPLE_SUBMITTER_HASH)
        submitter.save()
        proj = Projects()
        TestProjects.base_create_dep_objs()
        proj.from_hash(SAMPLE_PROJECT_HASH)
        proj.save(force_insert=True)
        inst = Instruments()
        TestInstruments.base_create_dep_objs()
        inst.from_hash(SAMPLE_INSTRUMENT_HASH)
        inst.save(force_insert=True)
        trans = Transactions()
        TestTransactions.base_create_dep_objs()
        trans.from_hash(SAMPLE_TRANSACTION_HASH)
        trans.save(force_insert=True)

    def test_transsip_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_TRANSSIP_HASH)

    def test_transsip_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_TRANSSIP_HASH))

    def test_transsip_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_TRANSSIP_HASH)
