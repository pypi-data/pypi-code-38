#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the files ORM object."""
from datetime import datetime, timedelta
from json import dumps
from pacifica.metadata.orm.utils import datetime_now_nomicrosecond
from pacifica.metadata.orm.files import Files
from pacifica.metadata.orm.transactions import Transactions
from .base_test import TestBase
from .transactions_test import SAMPLE_TRANSACTION_HASH, TestTransactions

SAMPLE_FILE_HASH = {
    '_id': 127,
    'name': 'test.txt',
    'subdir': 'a/b',
    'mimetype': 'text/plain',
    'mtime': datetime_now_nomicrosecond().isoformat(),
    'ctime': datetime_now_nomicrosecond().isoformat(),
    'hashtype': 'sha1',
    'hashsum': 'd8ff327b2f643130b431ae7c1f1b1e191bc419af',
    'size': 1234,
    'transaction': SAMPLE_TRANSACTION_HASH['_id'],
    'suspense_date': datetime.utcnow().date().isoformat(),
    'encoding': 'UTF8'
}

SAMPLE_UNICODE_FILE_HASH = {
    '_id': 127,
    'name': u'abcdé.txt',
    'subdir': u'abcdé/b',
    'mimetype': 'text/plain',
    'mtime': datetime_now_nomicrosecond().isoformat(),
    'ctime': datetime_now_nomicrosecond().isoformat(),
    'hashtype': 'sha1',
    'hashsum': 'd8ff327b2f643130b431ae7c1f1b1e191bc419af',
    'size': 1234,
    'transaction': SAMPLE_TRANSACTION_HASH['_id'],
    'suspense_date': datetime.utcnow().date().isoformat(),
    'encoding': 'UTF8'
}


class TestFiles(TestBase):
    """Test the Files ORM object."""

    obj_cls = Files
    obj_id = Files.id

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that Files depend on."""
        trans = Transactions()
        TestTransactions.base_create_dep_objs()
        trans.from_hash(SAMPLE_TRANSACTION_HASH)
        trans.save(force_insert=True)

    def test_unicode_files_hash(self):
        """Test the unicode hash using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_FILE_HASH)

    def test_files_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_FILE_HASH)

    def test_files_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_FILE_HASH))

    def test_files_search_expr(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_FILE_HASH,
            name_operator='ILIKE',
            name=u'%é%'
        )

    def test_files_search_time(self):
        """Test the hash portion using base object method."""
        date_time_chk = datetime.utcnow() - timedelta(minutes=10)
        self.base_where_clause_search_expr(
            SAMPLE_FILE_HASH,
            mtime_operator='GT',
            mtime=date_time_chk.replace(microsecond=0).isoformat()
        )

    def test_files_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_FILE_HASH)

    def test_unicode_files_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_FILE_HASH)
