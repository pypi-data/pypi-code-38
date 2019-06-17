
##########################################################################
## Imports
##########################################################################

import pytest
from btrdb_admin import connect
from btrdb_admin.exceptions import *
from tests.conftest import get_db_conn

USERS = ['admin', 'bbengfort', 'public', 'test']
TEST_ACCOUNT = "marmaduke"
TEST_PASSWORD = "usiB6iUsRLyng3mUcTcCpwdZ69sag"
TEST_GROUP = "testaclgroup"

##########################################################################
## Tests
##########################################################################

class TestACL(object):

    @classmethod
    def setup_class(cls):
        db = get_db_conn()
        if db.user_exists(TEST_ACCOUNT):
            db.delete_user(TEST_ACCOUNT)

        try:
            group = db.get_group(TEST_GROUP)
            db.delete_group(TEST_GROUP)
        except BTRDBError:
            pass


    @classmethod
    def teardown_class(cls):
        db = get_db_conn()
        if db.user_exists(TEST_ACCOUNT):
            db.delete_user(TEST_ACCOUNT)


    ##########################################################################
    ## User Tests
    ##########################################################################

    def test_all_users(self, db):
        users = db.get_all_users()
        assert users == USERS


    def test_user_exists(self, db):
        val = db.user_exists("admin")
        assert val is True

        val = db.user_exists("marypoppins")
        assert val is False


    def test_get_api_key(self, db):
        apikey = db.get_api_key("admin")
        assert len(apikey) > 0
        assert isinstance(apikey, str)


    def test_user_flow(self, db):

        # user doesnt already exist
        assert db.user_exists(TEST_ACCOUNT) is False

        # create user
        db.create_user(TEST_ACCOUNT, TEST_PASSWORD)
        assert db.user_exists(TEST_ACCOUNT) is True

        # get apikey
        apikey = db.get_api_key(TEST_ACCOUNT)

        # auth by apikey
        user = db.authenticate_user_by_key(apikey)
        assert user.username == TEST_ACCOUNT

        # auth by username/password
        user = db.authenticate_user(TEST_ACCOUNT, TEST_PASSWORD)
        assert user.username == TEST_ACCOUNT

        # reset apikey
        new_apikey = db.reset_api_key(TEST_ACCOUNT)
        assert new_apikey is not apikey
        assert len(new_apikey) > 0
        assert new_apikey.__class__ == str

        # user retrieval
        user = db.get_builtin_user(TEST_ACCOUNT)
        assert user['username'] == TEST_ACCOUNT
        assert user['groups'] == [{'name': 'public', 'prefixes': [''], 'capabilities': [3, 4, 5, 6, 0, 1, 2]}]

        # delete user
        db.delete_user(TEST_ACCOUNT)
        assert db.user_exists(TEST_ACCOUNT) is False

        # verify delete
        assert db.get_all_users() == USERS


    ##########################################################################
    ## Group Tests
    ##########################################################################

    def test_get_all_groups(self, db):
        assert db.get_all_groups() == ['admin', 'public']


    def test_get_group(self, db):
        group = db.get_group('public')
        assert  group == {'capabilities': [3, 4, 5, 6, 0, 1, 2], 'name': 'public', 'prefixes': ['']}


    def test_group_flow(self, db):
        db.create_group(TEST_GROUP)

        db.create_user(TEST_ACCOUNT, TEST_PASSWORD)
        db.add_user_to_group(TEST_ACCOUNT, TEST_GROUP)
        user = db.get_builtin_user(TEST_ACCOUNT)
        assert user['groups'] == [
            {'name': TEST_GROUP, 'prefixes': [], 'capabilities': []},
            {'name': 'public', 'prefixes': [''], 'capabilities': [3, 4, 5, 6, 0, 1, 2]},
        ]

        db.remove_user_from_group(TEST_ACCOUNT, TEST_GROUP)
        user = db.get_builtin_user(TEST_ACCOUNT)
        assert user['groups'] == [
            {'name': 'public', 'prefixes': [''], 'capabilities': [3, 4, 5, 6, 0, 1, 2]},
        ]

        db.delete_user(TEST_ACCOUNT)

        group = db.get_group(TEST_GROUP)
        assert group == {'capabilities': [], 'name': 'testaclgroup', 'prefixes': []}

        db.set_group_prefixes(TEST_GROUP, ['cat', 'dog'])
        db.set_group_capabilities(TEST_GROUP, [0,1,2,3,4])
        group = db.get_group(TEST_GROUP)
        assert group == {'capabilities': [0,1,2,3,4], 'name': 'testaclgroup', 'prefixes': ['cat', 'dog']}

        db.delete_group(TEST_GROUP)
        with pytest.raises(BTRDBError):
            db.get_group(TEST_GROUP)
