#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the keys ORM object."""
from json import dumps
from datetime import datetime
from pacifica.metadata.orm.transactions import Transactions
from .base_test import TestBase

SAMPLE_TRANSACTION_HASH = {
    '_id': 127,
    'description': 'The really important description of the file content',
    'suspense_date': datetime.utcnow().date().isoformat()
}


class TestTransactions(TestBase):
    """Test the Transactions ORM object."""

    obj_cls = Transactions
    obj_id = Transactions.id

    def test_transactions_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_TRANSACTION_HASH)

    def test_transactions_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_TRANSACTION_HASH))

    def test_transactions_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_TRANSACTION_HASH)
