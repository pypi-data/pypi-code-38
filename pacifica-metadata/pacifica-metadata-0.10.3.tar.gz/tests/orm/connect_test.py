#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the connection logic see that it works as expected."""
import os
from unittest import TestCase
from peewee import SqliteDatabase, OperationalError
import pacifica.metadata.orm.sync as orm_sync


class TestConnections(TestCase):
    """Test connecting to databases make sure it works."""

    def test_db_connect_and_fail(self):
        """Try to connect to a database and fail."""
        orm_sync.DB = SqliteDatabase('file:///root/foo.db')
        os.environ['DATABASE_CONNECT_ATTEMPTS'] = '1'
        os.environ['DATABASE_CONNECT_WAIT'] = '1'
        hit_exception = False
        try:
            orm_sync.OrmSync.dbconn_blocking()
        except OperationalError:
            hit_exception = True
        self.assertTrue(hit_exception)
