# -*- coding: utf-8 -*-
# :Project:   PatchDB -- MySQL specific test
# :Created:   gio 25 feb 2016 14:32:05 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

import subprocess

try:
    import pymysql

    try:
        subprocess.check_call(['mysql', '--version'])
    except:
        raise ImportError('No MySQL client')
except ImportError:
    pass
else:
    import fixtures
    import test_sql
    import test_states

    DBNAME = 'mp-s-patchdb-test'

    class MSMixin(object):
        DB_OPTION = '--mysql'
        DB_NAME = DBNAME

        @classmethod
        def drop_database_if_exists(cls):
            p = subprocess.Popen(['mysql'], stdin=subprocess.PIPE)
            p.communicate(input=("drop database if exists `%s`" % DBNAME).encode('ascii'))

        @classmethod
        def create_database(cls):
            p = subprocess.Popen(['mysql'], stdin=subprocess.PIPE)
            (out, err) = p.communicate(input=("create database `%s`" % DBNAME).encode('ascii'))
            assert p.returncode == 0, out

    class TestSingleSQLScript(MSMixin, test_sql.TestSingleSQLScript):
        pass

    class TestMultiSQLScriptIgnoringErrors(MSMixin,
                                           test_sql.TestMultiSQLScriptIgnoringErrors):
        pass

    class TestFakeDomains(MSMixin, fixtures.BaseTestCase):
        TEST_TXT = """
        MySQL fake domains
        ==================

        .. patchdb:script:: Data domains
           :always: first

           CREATE DOMAIN id_t integer
           ;;
           CREATE DOMAIN value_t varchar(10)
           ;;
           CREATE DOMAIN `VALUE_T` varchar(100)

        .. patchdb:script:: Create table
           :depends: Data domains

           CREATE TABLE test (
             id id_t NOT NULL PRIMARY KEY,
             value value_t default 'VALUE_T',
             value_1 VALUE_T,
             longvalue `VALUE_T`
           )

        .. patchdb:script:: Add one more column
           :depends: Create table

           ALTER TABLE test
                 ADD another value_t NOT NULL DEFAULT 'X'

        .. patchdb:script:: Remove constraint
           :depends: Add one more column

           ALTER TABLE test
                 CHANGE another another value_t NULL DEFAULT NULL
        """

        def test(self):
            output = self.patchdb()
            self.assertIn('Done, applied 4 script', output)
            output = self.patchdb()
            self.assertIn('Done, applied 1 script', output)
            c, _ = self.get_connection_and_base_exception()
            try:
                q = c.cursor()
                q.execute('describe test')
                r = q.fetchone()
                self.assertEqual(r[1], 'int(11)')
                r = q.fetchone()
                self.assertEqual(r[1], 'varchar(10)')
                self.assertEqual(r[4], 'VALUE_T')
                r = q.fetchone()
                self.assertEqual(r[1], 'varchar(10)')
                r = q.fetchone()
                self.assertEqual(r[1], 'varchar(100)')
                r = q.fetchone()
                self.assertEqual(r[0], 'another')
                self.assertEqual(r[1], 'varchar(10)')
                self.assertEqual(r[2], 'YES')
                self.assertEqual(r[4], None)
            finally:
                c.close()

    class TestStates(MSMixin, test_states.TestStates):
        pass

    class TestRestoreState(MSMixin, test_states.TestRestoreState):
        pass

    class TestDropNonExistingTable(MSMixin, test_sql.TestDropNonExistingTable):
        pass

    class TestRevokeAllPrivileges(MSMixin, fixtures.BaseTestCase):
        TEST_TXT = """
        Ignore revoking non granted privileges
        ======================================

        .. patchdb:script:: Create first table

           create table sl_test (
             id integer primary key
           )

        .. patchdb:script:: Revoke all privileges
           :depends: Create first table

           revoke all privileges on table sl_test from 'ququ'

        .. patchdb:script:: Revoke all privileges on table again
           :depends: Revoke all privileges

           revoke all privileges on table sl_test from 'ququ'
        """
        NUM_OF_SCRIPTS = 3
