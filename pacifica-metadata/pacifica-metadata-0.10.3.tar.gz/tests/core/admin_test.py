#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the admin tools methods."""
from argparse import Namespace
from datetime import timedelta
from unittest import TestCase
from mock import patch
from peewee import SqliteDatabase, DoesNotExist
import pacifica.metadata.orm.globals as orm_db_mod
import pacifica.metadata.orm.all_objects as orm_obj_mod
from pacifica.metadata.orm.sync import OrmSync, MetadataSystem
from pacifica.metadata.admin_cmd import render_obj, create_table, bool2cmdint, delete_obj
from pacifica.metadata.admin_cmd import objstr_to_ormobj, objstr_to_whereclause, objstr_to_timedelta


class TestAdminTool(TestCase):
    """Test the admin tool cli."""

    def setUp(self):
        """Setup the database with in memory sqlite."""
        orm_db_mod.DB = SqliteDatabase(':memory:')
        for model in orm_obj_mod.ORM_OBJECTS:
            model.bind(orm_db_mod.DB, bind_refs=False, bind_backrefs=False)
        MetadataSystem.bind(orm_db_mod.DB, bind_refs=False,
                            bind_backrefs=False)
        orm_db_mod.DB.connect()
        orm_db_mod.DB.create_tables(orm_obj_mod.ORM_OBJECTS)
        MetadataSystem.create_table()
        MetadataSystem.get_or_create_version()

    def tearDown(self):
        """Tear down the database."""
        orm_db_mod.DB.drop_tables(orm_obj_mod.ORM_OBJECTS)
        orm_db_mod.DB.close()
        orm_db_mod.DB = None

    def test_bool2cmdint(self):
        """Test the bool2cmdint method."""
        self.assertEqual(-1, bool2cmdint(False))
        self.assertEqual(0, bool2cmdint(True))

    def test_objstr_to_timedelta(self):
        """Test the string object to timedelta object."""
        ten_minutes = objstr_to_timedelta('10 minutes ago')
        self.assertEqual(ten_minutes, timedelta(minutes=10))

    def test_objstr_to_ormobj(self):
        """Test the string object to ORM object type check."""
        cls = objstr_to_ormobj('Keys')
        self.assertEqual(cls, orm_obj_mod.Keys)
        hit_exception = False
        try:
            objstr_to_ormobj('Blah!')
        except ValueError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_objstr_to_whereclause(self):
        """Test the string object to ORM where clause parsing."""
        where_clause = objstr_to_whereclause('{"_id": 1234}')
        self.assertTrue(isinstance(where_clause, dict))
        hit_exception = False
        try:
            objstr_to_whereclause('[]')
        except ValueError:
            hit_exception = True
        self.assertTrue(hit_exception)

    @patch.object(OrmSync, 'dbconn_blocking')
    def test_delete(self, test_patch):
        """Test delete an object."""
        test_patch.return_value = True
        args = Namespace()
        setattr(args, 'object', orm_obj_mod.Keys)
        setattr(args, 'where_clause', {'key': 'test_key'})
        setattr(args, 'recursive', True)
        setattr(args, 'force', True)
        test_obj = orm_obj_mod.Keys()
        test_obj.key = 'test_key'
        test_obj.save()
        delete_obj(args)
        self.assertTrue(test_patch.called)
        with self.assertRaises(DoesNotExist):
            orm_obj_mod.Keys().get()

    @patch.object(OrmSync, 'dbconn_blocking')
    def test_render(self, test_patch):
        """Test render an object."""
        test_patch.return_value = True
        args = Namespace()
        setattr(args, 'object', orm_obj_mod.Keys)
        setattr(args, 'where_clause', {'key': 'test_key'})
        setattr(args, 'recursion', 1)
        test_obj = orm_obj_mod.Keys()
        test_obj.key = 'test_key'
        test_obj.save()
        render_obj(args)
        self.assertTrue(test_patch.called)

    @patch.object(OrmSync, 'dbconn_blocking')
    def test_create(self, test_patch):
        """Test the create obj."""
        test_patch.return_value = True
        self.assertTrue(MetadataSystem.is_equal())
        args = Namespace()
        setattr(args, 'object', orm_obj_mod.Keys)
        create_table(args)
        self.assertTrue(test_patch.called)


class TestAdminToolNoTables(TestCase):
    """Test the admin tool cli."""

    def setUp(self):
        """Setup the database with in memory sqlite."""
        orm_db_mod.DB = SqliteDatabase('file:cachedb?mode=memory&cache=shared')
        for model in orm_obj_mod.ORM_OBJECTS:
            model.bind(orm_db_mod.DB, bind_refs=False, bind_backrefs=False)
        orm_db_mod.DB.connect()

    def tearDown(self):
        """Tear down the database."""
        orm_db_mod.DB.drop_tables(orm_obj_mod.ORM_OBJECTS)
        MetadataSystem.drop_table()
        orm_db_mod.DB.close()
        orm_db_mod.DB = None

    @patch.object(OrmSync, 'dbconn_blocking')
    def test_create_no_tables(self, test_patch):
        """Test the create obj."""
        test_patch.return_value = True
        args = Namespace()
        setattr(args, 'object', orm_obj_mod.Keys)
        create_table(args)
        self.assertTrue(test_patch.called)
