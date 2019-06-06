#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the trans_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.trans_key_value import TransactionKeyValue
from pacifica.metadata.orm.transactions import Transactions
from pacifica.metadata.orm.keys import Keys
from pacifica.metadata.orm.values import Values
from .base_test import TestBase
from .transactions_test import SAMPLE_TRANSACTION_HASH, TestTransactions
from .keys_test import SAMPLE_KEY_HASH, TestKeys
from .values_test import SAMPLE_VALUE_HASH, TestValues

SAMPLE_TRANSACTION_KEY_VALUE_HASH = {
    'transaction': SAMPLE_TRANSACTION_HASH['_id'],
    'key': SAMPLE_KEY_HASH['_id'],
    'value': SAMPLE_VALUE_HASH['_id']
}


class TestTransactionKeyValue(TestBase):
    """Test the Keys ORM object."""

    obj_cls = TransactionKeyValue
    obj_id = TransactionKeyValue.transaction

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that TransactionKeyValue need."""
        trans = Transactions()
        keys = Keys()
        values = Values()
        TestTransactions.base_create_dep_objs()
        trans.from_hash(SAMPLE_TRANSACTION_HASH)
        trans.save(force_insert=True)
        TestKeys.base_create_dep_objs()
        keys.from_hash(SAMPLE_KEY_HASH)
        keys.save(force_insert=True)
        TestValues.base_create_dep_objs()
        values.from_hash(SAMPLE_VALUE_HASH)
        values.save(force_insert=True)

    def test_trans_key_value_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_TRANSACTION_KEY_VALUE_HASH)

    def test_trans_key_value_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_TRANSACTION_KEY_VALUE_HASH))

    def test_trans_key_value_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_TRANSACTION_KEY_VALUE_HASH)
