#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date:   Tue May 17 12:09:22 CET 2016
#

import os
import bob.io.base
import bob.io.base.test_utils
import bob.pad.base.database
import bob.db.base

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

regenerate_database = False

dbfile = bob.io.base.test_utils.datafile("test_db.sql3", "bob.pad.base.test", path="data")

Base = declarative_base()


class TestFileSql (Base, bob.pad.base.database.PadFile):
    __tablename__ = "file"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, unique=True)
    path = Column(String(100), unique=True)

    def __init__(self):
        bob.pad.base.database.PadFile.__init__(
            self, client_id=5, path="test/path")


def create_database():
    if os.path.exists(dbfile):
        os.remove(dbfile)
    import bob.db.base.utils
    engine = bob.db.base.utils.create_engine_try_nolock(
        'sqlite', dbfile, echo=True)
    Base.metadata.create_all(engine)
    session = bob.db.base.utils.session('sqlite', dbfile, echo=True)
    session.add(TestFileSql())
    session.commit()
    session.close()
    del session
    del engine


class TestDatabaseSql (bob.pad.base.database.PadDatabase, bob.db.base.SQLiteBaseDatabase):

    def __init__(self):
        super(TestDatabaseSql, self).__init__(
            name='pad_test',
            original_directory="original/directory",
            original_extension=".orig", sqlite_file=dbfile,
            file_class=TestFileSql)

    def groups(self, protocol=None):
        return ['group']

    def objects(self, groups=None, protocol=None, purposes=None, model_ids=None, **kwargs):
        return list(self.query(TestFileSql))

    def annotations(self, file):
        return None


database = TestDatabaseSql()
