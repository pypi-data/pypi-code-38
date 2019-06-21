# -*- coding: utf-8 -*-
# :Project:   PatchDB -- PG specific SQL statements test
# :Created:   mar 23 feb 2016 00:08:50 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

import subprocess

try:
    import psycopg2
except ImportError:
    pass
else:
    import fixtures
    import test_sql
    import test_states

    DBNAME = 'mp-s-patchdb-test'

    class PGMixin(object):
        DB_OPTION = '--postgresql'
        DB_NAME = 'dbname=' + DBNAME

        @classmethod
        def drop_database_if_exists(cls):
            subprocess.call(['dropdb', '--if-exists', DBNAME])

        @classmethod
        def create_database(cls):
            subprocess.check_call(['createdb', '-E', 'UTF-8', '-T', 'template0', DBNAME])

    class TestSingleSQLScript(PGMixin, test_sql.TestSingleSQLScript):
        pass

    class TestMultiSQLScriptIgnoringErrors(PGMixin,
                                           test_sql.TestMultiSQLScriptIgnoringErrors):
        pass

    class TestStates(PGMixin, test_states.TestStates):
        pass

    class TestRestoreState(PGMixin, test_states.TestRestoreState):
        pass

    class TestDropNonExistingTable(PGMixin, test_sql.TestDropNonExistingTable):
        pass

    class TestRevokeAllPrivileges(PGMixin, fixtures.BaseTestCase):
        TEST_TXT = """
        Ignore revoking non granted privileges
        ======================================

        .. patchdb:script:: Create first table

           create table sl_test (
             id integer primary key
           )

        .. patchdb:script:: Revoke all privileges
           :depends: Create first table

           revoke all privileges on table sl_test from public

        .. patchdb:script:: Revoke all privileges on table again
           :depends: Revoke all privileges

           revoke all privileges on table sl_test from public
        """
        NUM_OF_SCRIPTS = 3

    class TestAutocommitScript(PGMixin, fixtures.BaseTestCase):
        TEST_TXT = """
        Some SQL statements cannot be executed within a transaction
        ===========================================================

        .. patchdb:script:: Create empty enum

           create type my_enum as enum ()

        .. patchdb:script:: Add an item to the enum
           :depends: Create empty enum
           :autocommit:

           alter type my_enum add value 'foo'
        """
        NUM_OF_SCRIPTS = 2
