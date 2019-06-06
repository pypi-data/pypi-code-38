#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the file_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.citation_transaction import CitationTransaction
from pacifica.metadata.orm.citations import Citations
from pacifica.metadata.orm.transaction_user import TransactionUser
from .base_test import TestBase
from .citations_test import SAMPLE_CITATION_HASH, TestCitations
from .transaction_user_test import SAMPLE_TRANS_USER_HASH, TestTransactionUser

SAMPLE_CITATION_TRANS_HASH = {
    'citation': SAMPLE_CITATION_HASH['_id'],
    'transaction': SAMPLE_TRANS_USER_HASH['uuid']
}


class TestCitationTransaction(TestBase):
    """Test the Keywords ORM object."""

    obj_cls = CitationTransaction
    obj_id = CitationTransaction.citation

    @classmethod
    def base_create_dep_objs(cls):
        """Build the object and make dependent user object."""
        cite = Citations()
        TestCitations.base_create_dep_objs()
        cite.from_hash(SAMPLE_CITATION_HASH)
        cite.save(force_insert=True)
        trans_rel = TransactionUser()
        TestTransactionUser.base_create_dep_objs()
        trans_rel.from_hash(SAMPLE_TRANS_USER_HASH)
        trans_rel.save(force_insert=True)

    def test_citationtransaction_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_CITATION_TRANS_HASH)

    def test_citationtransaction_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_CITATION_TRANS_HASH))

    def test_citationtransaction_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_CITATION_TRANS_HASH)
