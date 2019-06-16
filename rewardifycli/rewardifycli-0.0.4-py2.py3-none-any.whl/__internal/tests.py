# standard library
import unittest

from typing import Dict, List

# third party
from click.testing import CliRunner

from rewardify.models import User

from rewardify._util_test import DBTestMixin, ConfigTestMixin

from rewardifycli.util import UserCredentials


# ################
# BEHAVIOUR MIXINS
# ################


class CLITestMixin:
    """
    This is a mixin, which implements, that a new click CLIRunner object is being created before every test is being
    run. The runner object will be saved in the class variable "RUNNER"

    CHANGELOG

    Added 14.06.2019
    """

    RUNNER = None

    def setUp(self):
        """
        This method is being called before every test that is being run. It will create a new CLIRunner instance and
        saves it in self.RUNNER

        CHANGELOG

        Added 14.06.2019

        :return:
        """
        self.RUNNER = CliRunner()


# ########################
# ACTUAL TEST BASE CLASSES
# ########################

class CLITestCase(CLITestMixin, unittest.TestCase):
    """
    This test case will create a new CLIRunner object before every test, which can be used to invoke click commands
    from within the code.

    CHANGELOG

    Added 14.06.2019
    """
    def setUp(self):
        CLITestMixin.setUp(self)


class RewardifycliTestCase(CLITestMixin, ConfigTestMixin, DBTestMixin, unittest.TestCase):

    def setUp(self):
        DBTestMixin.setUp(self)
        ConfigTestMixin.setUp(self)
        CLITestMixin.setUp(self)

    def tearDown(self):
        DBTestMixin.tearDown(self)


# ####################################
# CONTEXT MANAGERS FOR SPECIFIC SETUPS
# ####################################


class MockConfigContext:

    IMPORTS = [
        'from rewardify.backends import AbstractBackend'
    ]
    DATABASE_DICT = {
        'engine': 'sqlite',
        'host': ':memory:',
        'database': '',
        'user': '',
        'password': '',
        'port': 0
    }
    PACKS = [
        {
            'name':         'Standard Pack',
            'cost':         100,
            'description': 'for testing',
            'slot1':        [1, 0, 0, 0],
            'slot2':        [1, 0, 0, 0],
            'slot3':        [1, 0, 0, 0],
            'slot4':        [1, 0, 0, 0],
            'slot5':        [1, 0, 0, 0],
        }
    ]
    REWARDS = [
        {
            'name':         'Standard Reward',
            'description':  'for testing',
            'rarity':       'uncommon',
            'cost':          100,
            'recycle':       100
        }
    ]
    BACKEND = 'MockBackend'
    MOCK_USERS = [
        'Jonas'
    ]

    def __init__(self,
                 test_case: ConfigTestMixin,
                 packs: List[Dict] = PACKS,
                 rewards: List[Dict] = REWARDS,
                 mock_users: List[str] = MOCK_USERS):
        self.test_case = test_case
        self.imports = self.IMPORTS.copy()
        self.database_dict = self.DATABASE_DICT.copy()
        self.packs = packs.copy()
        self.rewards = rewards.copy()
        self.users = mock_users.copy()
        self.backend = self.BACKEND
        self.plugin_code = self.create_plugin_code(self.users)
        self.credentials: UserCredentials = UserCredentials.instance()

    def update(self):
        self.test_case.clean()
        self.plugin_code = self.create_plugin_code(self.users)
        self.test_case.create_config(
            self.imports,
            self.database_dict,
            self.backend,
            self.rewards,
            self.packs,
            self.plugin_code
        )

    def __enter__(self):
        self.update()
        self.credentials.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.test_case.clean()

    @classmethod
    def create_plugin_code(cls, users: List[str]):
        users = list(map(lambda u: '"{}"'.format(u), users))
        return 'MOCK_BACKEND_USERS = [{}]'.format(','.join(users))


class StandardUserContext:

    USERNAME = 'Jonas'
    PASSWORD = 'secret'
    DUST = 0
    GOLD = 0

    def __init__(self):
        self.username = self.USERNAME
        self.password = self.PASSWORD
        self.dust = self.DUST
        self.gold = self.GOLD

        # This field will later contain the user object
        self.user: User = None

    def update(self):
        self.user = User.get(User.name == self.username)

    def __enter__(self):
        self.user = User(
            name=self.username,
            password=self.password,
            dust=self.dust,
            gold=self.gold
        )
        self.user.save()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.user.delete_instance(recursive=True)

