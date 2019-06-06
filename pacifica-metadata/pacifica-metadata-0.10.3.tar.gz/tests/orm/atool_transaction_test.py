#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the atool_transaction ORM object."""
from json import dumps
from pacifica.metadata.orm.atool_transaction import AToolTransaction
from pacifica.metadata.orm.transactions import Transactions
from pacifica.metadata.orm.analytical_tools import AnalyticalTools
from .base_test import TestBase
from .transactions_test import SAMPLE_TRANSACTION_HASH, TestTransactions
from .analytical_tools_test import SAMPLE_TOOL_HASH, TestAnalyticalTools

SAMPLE_TOOL_TRANS_HASH = {
    'transaction': SAMPLE_TRANSACTION_HASH['_id'],
    'analytical_tool': SAMPLE_TOOL_HASH['_id']
}


class TestAToolTransaction(TestBase):
    """Test the Keys ORM object."""

    obj_cls = AToolTransaction
    obj_id = AToolTransaction.transaction

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that TransactionKeyValue need."""
        trans = Transactions()
        tool = AnalyticalTools()
        TestTransactions.base_create_dep_objs()
        trans.from_hash(SAMPLE_TRANSACTION_HASH)
        trans.save(force_insert=True)
        TestAnalyticalTools.base_create_dep_objs()
        tool.from_hash(SAMPLE_TOOL_HASH)
        tool.save(force_insert=True)

    def test_tool_trans_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_TOOL_TRANS_HASH)

    def test_tool_trans_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_TOOL_TRANS_HASH))

    def test_tool_trans_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_TOOL_TRANS_HASH)
