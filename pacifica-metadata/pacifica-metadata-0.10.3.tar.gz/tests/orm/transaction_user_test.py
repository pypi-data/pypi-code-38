#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the file_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.transaction_user import TransactionUser
from pacifica.metadata.orm.transactions import Transactions
from pacifica.metadata.orm.relationships import Relationships
from pacifica.metadata.orm.users import Users
from .base_test import TestBase
from .transactions_test import SAMPLE_TRANSACTION_HASH, TestTransactions
from .users_test import SAMPLE_USER_HASH as SAMPLE_CREATOR_HASH
from .users_test import TestUsers
from .relationships_test import SAMPLE_RELATIONSHIP_HASH, TestRelationships

SAMPLE_TRANS_USER_HASH = {
    'uuid': 'e6adfbf6-b236-46d8-bafd-315516fb12d9',
    'user': SAMPLE_CREATOR_HASH['_id'],
    'relationship': SAMPLE_RELATIONSHIP_HASH['uuid'],
    'transaction': SAMPLE_TRANSACTION_HASH['_id']
}


class TestTransactionUser(TestBase):
    """Test the Keywords ORM object."""

    obj_cls = TransactionUser
    obj_id = TransactionUser.uuid

    @classmethod
    def base_create_dep_objs(cls):
        """Build the object and make dependent user object."""
        rel = Relationships()
        TestRelationships.base_create_dep_objs()
        rel.from_hash(SAMPLE_RELATIONSHIP_HASH)
        rel.save(force_insert=True)
        user3 = Users()
        TestUsers.base_create_dep_objs()
        user3.from_hash(SAMPLE_CREATOR_HASH)
        user3.save(force_insert=True)
        rel_trans = Transactions()
        TestTransactions.base_create_dep_objs()
        rel_trans.from_hash(SAMPLE_TRANSACTION_HASH)
        rel_trans.save(force_insert=True)

    def test_transuser_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_TRANS_USER_HASH)

    def test_transuser_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_TRANS_USER_HASH))

    def test_transuser_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_TRANS_USER_HASH)
