# standard library
import datetime

from typing import Dict, List

# local imports
from rewardify._util_test import RewardifyTestCase

from rewardify.backends import MockBackend

from rewardify.models import User, Pack, Reward

from rewardify.main import Rewardify
from rewardify.main import available_rewards, available_rewards_by_rarity
from rewardify.main import open_pack


class TestMain(RewardifyTestCase):

    # SAMPLE VALUES FOR THE ENVIRONMENT CONFIG
    # ----------------------------------------

    SAMPLE_IMPORTS = [
        'from rewardify.backends import AbstractBackend'
    ]

    SAMPLE_DATABASE_DICT = {
        'engine': 'sqlite',
        'host': ':memory:',
        'database': '',
        'user': '',
        'password': '',
        'port': 0
    }

    SAMPLE_PACKS = [
        {
            'name':             'Sample Pack',
            'cost':             100,
            'description':      'for testing',
            'slot1':            [1, 0, 0, 0],
            'slot2':            [1, 0, 0, 0],
            'slot3':            [1, 0, 0, 0],
            'slot4':            [1, 0, 0, 0],
            'slot5':            [1, 0, 0, 0],
        }
    ]

    SAMPLE_REWARDS = [
        {
            'name':             'Sample Reward',
            'description':      'for testing',
            'rarity':           'uncommon',
            'cost':             100,
            'recycle':          100
        }
    ]

    SAMPLE_BACKEND = 'MockBackend'

    SAMPLE_PLUGIN_CODE = 'MOCK_BACKEND_USERS = ["Jonas"]'

    # SAMPLE DATABASE VALUES
    # ----------------------

    SAMPLE_USER_PARAMETERS = {
        'name':     'Jonas',
        'password':     'secret',
        'gold':         0,
        'dust':         0
    }

    # TESTING BUSINESS LOGIC FUNCTIONS
    # --------------------------------

    def test_available_rewards(self):
        # For the available rewards we need to config environment
        self.setup_sample()

        rewards = available_rewards()
        filtered_rewards = list(filter(lambda d: d['name'] == 'Sample Reward', rewards))
        self.assertEqual(len(filtered_rewards), 1)

    def test_available_rewards_by_rarity(self):
        self.setup_sample()

        rarity_reward_map = available_rewards_by_rarity()
        self.assertEqual(len(rarity_reward_map['uncommon']), 1)
        self.assertEqual(len(rarity_reward_map['legendary']), 0)

    def test_open_pack(self):
        self.setup_sample()
        self.create_sample_user()
        user = self.get_sample_user()

        pack_parameters = {
            'name':             'Sample Pack',
            'slug':             'sample_pack',
            'description':      'testing',
            'gold_cost':        100,
            'date_obtained':    datetime.datetime.now(),
            'slot1':            [1, 0, 0, 0],
            'slot2':            [1, 0, 0, 0],
            'slot3':            [1, 0, 0, 0],
            'slot4':            [1, 0, 0, 0],
            'slot5':            [1, 0, 0, 0],
        }

        # First we need to give the user one pack
        user.add_pack(pack_parameters)

        open_pack(
            self.SAMPLE_USER_PARAMETERS['name'],
            'Sample Pack'
        )

        self.assertEqual(len(user.packs), 0)
        self.assertEqual(len(user.rewards), 5)

    # TESTING FACADE OBJECT
    # ---------------------

    def test_test_case_working(self):
        self.setup_sample()

        # Now if everything was setup correctly the config instance from within the facade object should contain all
        # the sample values
        facade = Rewardify.instance()
        self.assertTrue(hasattr(facade.CONFIG, "BACKEND"))
        self.assertEqual(facade.CONFIG.BACKEND, MockBackend)

    def test_creating_new_user(self):
        facade: Rewardify = Rewardify.instance()

        # Creating the user
        username = 'Nigel'
        password = 'snobby'
        facade.create_user(username, password)

        # Querying for the user to check if it exists
        query = User.select().where(User.name == username)
        self.assertTrue(len(query) >= 1)
        user = query[0]
        self.assertTrue(user.password.check(password))

    def test_checking_password_to_username(self):
        # Setting up the environment and Inserting a new user into the database
        self.setup_sample()
        self.create_sample_user()

        facade: Rewardify = Rewardify.instance()
        facade.user_check_password(
            self.SAMPLE_USER_PARAMETERS['name'],
            self.SAMPLE_USER_PARAMETERS['password']
        )

    def test_getting_user_model_from_facade(self):
        # Setting up the environment and Inserting a new user into the database
        self.setup_sample()
        self.create_sample_user()

        facade: Rewardify = Rewardify.instance()
        user = facade.get_user(self.SAMPLE_USER_PARAMETERS['name'])
        self.assertIsInstance(user, User)

    def test_available_packs(self):
        self.setup_sample()

        facade: Rewardify = Rewardify.instance()
        available_packs: List = facade.available_packs()
        self.assertTrue(len(available_packs), 2)

    def test_backend_update(self):
        self.setup_sample()
        self.create_sample_user()
        user = self.get_sample_user()
        self.assertEqual(user.gold, 0)

        facade: Rewardify = Rewardify.instance()
        facade.backend_update()

        # The mock backend gives every user specified in MOCK_BACKEND_USERS exactly 100 gold on every call of the
        # update, which means, that after the call the user should have been granted 100 gold from the mock backend.
        user = self.get_sample_user()
        self.assertEqual(user.gold, 100)

    def test_user_exists(self):
        self.setup_sample()
        facade: Rewardify = Rewardify.instance()

        # Of course from the get go the user is not in the database, which means the exists call should return false
        user_exists = facade.exists_user(self.SAMPLE_USER_PARAMETERS['name'])
        self.assertFalse(user_exists)

        # After we have inserted the user though the exists call should return true
        self.create_sample_user()
        user_exists = facade.exists_user(self.SAMPLE_USER_PARAMETERS['name'])
        self.assertTrue(user_exists)

    # HELPER METHODS
    # --------------

    def setup_sample(self):
        # Setting up the config file with the sample values
        self.create_config(
            self.SAMPLE_IMPORTS,
            self.SAMPLE_DATABASE_DICT,
            self.SAMPLE_BACKEND,
            self.SAMPLE_REWARDS,
            self.SAMPLE_PACKS,
            self.SAMPLE_PLUGIN_CODE
        )

    def create_sample_user(self):
        user = User(**self.SAMPLE_USER_PARAMETERS)
        user.save()

    def get_sample_user(self) -> User:
        user = User.get(User.name == self.SAMPLE_USER_PARAMETERS['name'])
        return user
