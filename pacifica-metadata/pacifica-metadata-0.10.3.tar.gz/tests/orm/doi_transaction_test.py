#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the file_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.doi_transaction import DOITransaction
from pacifica.metadata.orm.doi_entries import DOIEntries
from pacifica.metadata.orm.transaction_user import TransactionUser
from .base_test import TestBase
from .doi_entries_test import SAMPLE_DOIENTRIES_HASH
from .transaction_user_test import SAMPLE_TRANS_USER_HASH, TestTransactionUser

SAMPLE_DOI_TRANS_HASH = {
    'doi': SAMPLE_DOIENTRIES_HASH['doi'],
    'transaction': SAMPLE_TRANS_USER_HASH['uuid']
}


class TestDOITransaction(TestBase):
    """Test the Keywords ORM object."""

    obj_cls = DOITransaction
    obj_id = DOITransaction.doi

    @classmethod
    def base_create_dep_objs(cls):
        """Build the object and make dependent user object."""
        trans_rel = TransactionUser()
        TestTransactionUser.base_create_dep_objs()
        trans_rel.from_hash(SAMPLE_TRANS_USER_HASH)
        trans_rel.save(force_insert=True)

        doi_ds = DOIEntries()
        doi_ds.from_hash(SAMPLE_DOIENTRIES_HASH)
        doi_ds.save(force_insert=True)

    def test_doitransaction_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_DOI_TRANS_HASH)

    def test_doitransaction_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_DOI_TRANS_HASH))

    def test_doitransaction_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_DOI_TRANS_HASH)
