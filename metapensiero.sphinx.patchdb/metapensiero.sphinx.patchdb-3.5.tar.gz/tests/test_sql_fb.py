# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Firebird specific tests
# :Created:   dom 17 apr 2016 18:28:36 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

try:
    import fdb
    try:
        # FIXME: this obviously works only for me
        fdb.services.connect('localhost', 'lele', 'lele')
    except:
        raise ImportError('FB server not installed')
except ImportError:
    pass
else:
    import fixtures
    import test_sql
    import test_states

    class FBMixin(object):
        DB_OPTION = '--firebird'
        DB_NAME = 'localhost:/tmp/patchdb-test.fdb'
        # FIXME: this obviously works only for me
        DB_OTHER_OPTIONS = ('--username', 'lele', '--password', 'lele')
        USER = PASSWORD = 'lele'

        @classmethod
        def drop_database_if_exists(cls):
            try:
                c = fdb.connect(cls.DB_NAME, user=cls.USER, password=cls.PASSWORD)
            except:
                pass
            else:
                c.drop_database()

        @classmethod
        def create_database(cls):
            fdb.create_database("create database '%s' user '%s' password '%s'"
                                % (cls.DB_NAME, cls.USER, cls.PASSWORD))

    class TestSingleSQLScript(FBMixin, test_sql.TestSingleSQLScript):
        pass

    class TestMultiSQLScriptIgnoringErrors(FBMixin,
                                           test_sql.TestMultiSQLScriptIgnoringErrors):
        pass

    class TestStates(FBMixin, test_states.TestStates):
        pass

    class TestRestoreState(FBMixin, test_states.TestRestoreState):
        pass

    class TestDropNonExistingTable(FBMixin, test_sql.TestDropNonExistingTable):
        pass

    class TestRevokeAllPrivileges(FBMixin, fixtures.BaseTestCase):
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
        """
        NUM_OF_SCRIPTS = 2
