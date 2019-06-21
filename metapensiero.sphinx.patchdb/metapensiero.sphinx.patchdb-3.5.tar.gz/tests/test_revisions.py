# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Test for multiple revisions of script
# :Created:   mer 24 feb 2016 17:30:26 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

import fixtures


FIRST_REV = """
Multiple revisions
==================

.. patchdb:script:: Create first table

   create table test (
     id integer primary key
   )
"""

SECOND_REV = """
Multiple revisions
==================

.. patchdb:script:: Create first table
   :revision: 2

   create table test (
     id integer primary key,
     thevalue integer
   )

.. patchdb:script:: Update first table
   :depends: Create first table@1
   :brings: Create first table@2

   alter table test add thevalue integer
"""


class TestMultipleRevFromScratch(fixtures.BaseTestCase):
    TEST_TXT = SECOND_REV


class TestMultipleRevIncremental(fixtures.BaseTestCase):
    TEST_TXT = FIRST_REV

    def test_1(self):
        connection, exception = self.get_connection_and_base_exception()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute('select thevalue from test')
            except exception as e:
                assert 'THEVALUE' in str(e).upper()
            else:
                assert False, "Should have raised an exception of kind %r!" % exception
        finally:
            connection.close()

    def test_2(self):
        self.build({'test.txt': SECOND_REV})
        output = self.patchdb('--debug')
        self.assertIn('Done, applied 1 script', output)
        connection, exception = self.get_connection_and_base_exception()
        try:
            cursor = connection.cursor()
            cursor.execute('select thevalue from test')
        finally:
            connection.close()


OLD_TABLE = """
Old table
=========

.. patchdb:script:: Create old table

   create table old_table (
     id integer primary key
   )
"""

NEW_TABLE = """
New table
=========

.. patchdb:script:: Create old table
   :revision: 2

   drop table if exists old_table

.. patchdb:script:: Create new table

   create table new_table (
     id integer primary key,
     thevalue integer
   )

.. patchdb:script:: Replace table
   :depends: Create old table@1
   :brings:
     - Create old table@2
     - Create new table@1

   create table new_table (
     id integer primary key,
     thevalue integer
   )
   ;;
   insert into new_table (id, thevalue) select id, id*10 from old_table
   ;;
   drop table old_table
"""


class TestReplaceTableFromScratch(fixtures.BaseTestCase):
    TEST_TXT = NEW_TABLE
    NUM_OF_SCRIPTS = 2


OBSOLETED_PATCH = """
Obsolete patch
==============

.. patchdb:script:: Create new table

   create table new_table (
     id integer primary key,
     thevalue integer
   )

.. patchdb:script:: Create second table

   create table second_table (
     id integer primary key
   )

.. patchdb:script:: Replace table
   :depends: Create second table@1
   :brings:
     - Create new table@1
   :drops:
     - Create old table

   create table new_table (
     id integer primary key,
     thevalue integer
   )
   ;;
   insert into new_table (id, thevalue) select id, id*10 from old_table
   ;;
   drop table old_table
"""


class TestObsoletedPatch(fixtures.BaseTestCase):
    TEST_TXT = OBSOLETED_PATCH
    NUM_OF_SCRIPTS = 2


class TestReplaceTableIncremental(fixtures.BaseTestCase):
    TEST_TXT = OLD_TABLE

    def test_1(self):
        connection, exception = self.get_connection_and_base_exception()
        try:
            cursor = connection.cursor()
            cursor.execute('insert into old_table (id) values (1)')
            cursor.execute('insert into old_table (id) values (2)')
            connection.commit()
        finally:
            connection.close()

    def test_2(self):
        self.build({'test.txt': NEW_TABLE})
        output = self.patchdb('--debug')
        self.assertIn('Done, applied 1 script', output)
        connection, exception = self.get_connection_and_base_exception()
        try:
            cursor = connection.cursor()
            cursor.execute('select thevalue from new_table where id=1')
            row = cursor.fetchone()
            self.assertEqual(row[0], 10)
            try:
                cursor.execute('select id from old_table')
            except exception as e:
                assert 'OLD_TABLE' in str(e).upper()
            else:
                assert False, "Should have raised an exception of kind %r!" % exception
        finally:
            connection.close()


RENAME_TABLE = """
Renamed table
=============

.. patchdb:script:: Create new table

   create table new_table (
     id integer primary key
   )
   ;;
   insert into new_table (id) values (0)

.. patchdb:script:: Rename old_table to new_table
   :depends: Create old table@1
   :brings:
     - Create new table@1

   alter table old_table rename to new_table
   ;;
   insert into new_table (id) values (3)
"""


class TestRenameTableFromScratch(fixtures.BaseTestCase):
    TEST_TXT = RENAME_TABLE

    def test(self):
        output = self.patchdb()
        self.assertIn('Done, applied 1 script', output)
        connection, exception = self.get_connection_and_base_exception()
        try:
            cursor = connection.cursor()
            cursor.execute('select id from new_table where id=0')
            row = cursor.fetchone()
            self.assertEqual(row[0], 0)
        finally:
            connection.close()


class TestRenameTableIncremental(fixtures.BaseTestCase):
    TEST_TXT = OLD_TABLE

    def test_1(self):
        connection, exception = self.get_connection_and_base_exception()
        try:
            cursor = connection.cursor()
            cursor.execute('insert into old_table (id) values (1)')
            cursor.execute('insert into old_table (id) values (2)')
            connection.commit()
        finally:
            connection.close()

    def test_2(self):
        self.build({'test.txt': RENAME_TABLE})
        output = self.patchdb('--debug')
        self.assertIn('Done, applied 1 script', output)
        connection, exception = self.get_connection_and_base_exception()
        try:
            cursor = connection.cursor()
            cursor.execute('select id from new_table where id=0')
            row = cursor.fetchone()
            self.assertIsNone(row)
            cursor.execute('select id from new_table where id=1')
            row = cursor.fetchone()
            self.assertEqual(row[0], 1)
            cursor.execute('select id from new_table where id=3')
            row = cursor.fetchone()
            self.assertEqual(row[0], 3)
            try:
                cursor.execute('select id from old_table')
            except exception as e:
                assert 'OLD_TABLE' in str(e).upper()
            else:
                assert False, "Should have raised an exception of kind %r!" % exception
        finally:
            connection.close()
