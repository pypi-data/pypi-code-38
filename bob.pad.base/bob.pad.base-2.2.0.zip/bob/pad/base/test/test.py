#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date:   Tue May 17 12:09:22 CET 2016
#

import os
import shutil
import bob.io.base
import bob.io.base.test_utils
import bob.bio.base.database
import bob.pad.base.database
import bob.db.base

import tempfile
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

regenerate_database = False

dbfile = bob.io.base.test_utils.datafile("test_db.sql3", "bob.pad.base.test")

Base = declarative_base()


class TestFile (Base, bob.pad.base.database.PadFile):
    __tablename__ = "file"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, unique=True)
    path = Column(String(100), unique=True)

    def __init__(self):
        bob.pad.base.database.PadFile.__init__(self, client_id=5, path="test/path")


def create_database():
    if os.path.exists(dbfile):
        os.remove(dbfile)
    import bob.db.base.utils
    engine = bob.db.base.utils.create_engine_try_nolock('sqlite', dbfile, echo=True)
    Base.metadata.create_all(engine)
    session = bob.db.base.utils.session('sqlite', dbfile, echo=True)
    session.add(TestFile())
    session.commit()
    session.close()
    del session
    del engine


class TestDatabase (bob.pad.base.database.PadDatabase, bob.db.base.SQLiteDatabase):
    def __init__(self):
        bob.pad.base.database.PadDatabase.__init__(self, 'pad_test', original_directory="original/directory", original_extension=".orig")
        bob.db.base.SQLiteDatabase.__init__(self, dbfile, TestFile)

    def groups(self, protocol=None):
        return ['group']

    def objects(self, groups=None, protocol=None, purposes=None, model_ids=None, **kwargs):
        return list(self.query(TestFile))


# def test01_database():
#     # check that the database API works
#     if regenerate_database:
#         create_database()
#
#     db = TestDatabase()
#
#     def check_file(fs, l=1):
#         assert len(fs) == l
#         if l == 1:
#             f = fs[0]
#         else:
#             f = fs[0][0]
#         assert isinstance(f, TestFile)
#         assert f.id == 1
#         assert f.client_id == 5
#         assert f.path == "test/path"
#
#     check_file(db.objects())
#     check_file(db.all_files(), 2)
#     check_file(db.training_files(), 2)
#     check_file(db.files([1]))
#     check_file(db.reverse(["test/path"]))
#
#     file = db.objects()[0]
#     assert db.original_file_name(file) == "original/directory/test/path.orig"
#     assert db.file_names([file], "another/directory", ".other")[0] == "another/directory/test/path.other"
#     assert db.paths([1], "another/directory", ".other")[0] == "another/directory/test/path.other"
#
#     # try file save
#     temp_dir = tempfile.mkdtemp(prefix="bob_db_test_")
#     data = [1., 2., 3.]
#     file.save(data, temp_dir)
#     assert os.path.exists(file.make_path(temp_dir, ".hdf5"))
#     read_data = bob.io.base.load(file.make_path(temp_dir, ".hdf5"))
#     for i in range(3):
#         assert data[i] == read_data[i]
#     shutil.rmtree(temp_dir)
