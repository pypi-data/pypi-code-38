# standard library
import os
import shutil

# Third party
from rewardify.env import EnvironmentInstaller

from rewardify.main import Rewardify

# local
from rewardifycli.__internal.tests import CLITestCase
from rewardifycli.__internal.tests import RewardifycliTestCase
from rewardifycli.__internal.tests import StandardUserContext, MockConfigContext

from rewardifycli.util import Templater, UserCredentials

from rewardifycli.install import install, run

from rewardifycli.login import login

from rewardifycli.packs import packs

from rewardifycli.inventory import inventory

from rewardifycli.rewards import rewards

from rewardifycli.users import users


class TestInstall(CLITestCase):

    INSTALL_FOLDER = '/tmp/rewardify'

    def setUp(self):
        CLITestCase.setUp(self)
        # Before every test the installation folder has to be reset
        config_folder_path = self.get_config_folder_path()
        if os.path.exists(config_folder_path):
            shutil.rmtree(self.get_config_folder_path())

    def test_run_output(self):
        result = self.RUNNER.invoke(run, ['--path={}'.format(self.INSTALL_FOLDER)])

        self.assertEqual(result.exit_code, 0)
        self.assertTrue('INSTALLATION FINISHED' in result.output)

    def test_run_installation_successful(self):
        self.RUNNER.invoke(run, ['--path={}'.format(self.INSTALL_FOLDER)])

        installer: EnvironmentInstaller = EnvironmentInstaller(self.INSTALL_FOLDER)
        # If the installation has indeed worked, the folder and the two files 'config.py
        # and 'rewardify.db' have to exist now
        config_folder_path = installer.get_config_folder_path()
        self.assertTrue(os.path.exists(config_folder_path))
        self.assertTrue(os.path.isdir(config_folder_path))
        config_file_path = installer.get_config_file_path()
        self.assertTrue(os.path.exists(config_file_path))
        database_file_path = installer.get_database_file_path()
        self.assertTrue(os.path.exists(database_file_path))

    # HELPER METHODS
    # --------------

    def get_config_folder_path(self):
        installer: EnvironmentInstaller = EnvironmentInstaller(self.INSTALL_FOLDER)
        return installer.get_config_folder_path()


class TestLogin(RewardifycliTestCase):

    def test_generally_working(self):
        with MockConfigContext(self) as mock_context:
            result = self.RUNNER.invoke(login, ['Jonas', 'secret'])
            self.assertEqual(result.exit_code, 1)

    def test_user_not_exists(self):
        with MockConfigContext(self) as mock_context:
            result = self.RUNNER.invoke(login, ['Jonas', 'secret'])
            self.assertEqual(result.exit_code, 1)

            self.assertTrue('AUTHENTICATION FAILURE' in result.output)

    def test_user_password_incorrect(self):
        with MockConfigContext(self) as mock_context, StandardUserContext() as user_context:
            result = self.RUNNER.invoke(login, [user_context.username, "Wrong password"])
            self.assertEqual(result.exit_code, 1)

            self.assertTrue('AUTHENTICATION FAILURE' in result.output)
            self.assertTrue('PASSWORD' in result.output)

    def test_user_credentials_saved_correctly(self):
        with MockConfigContext(self) as mock_context, StandardUserContext() as user_context:
            credentials: UserCredentials = UserCredentials.instance()

            result = self.RUNNER.invoke(login, [user_context.username, user_context.password])
            self.assertEqual(result.exit_code, 0)

            self.assertTrue('USER AUTHENTICATED' in result.output)
            self.assertEqual(user_context.username, credentials['username'])


class TestPacks(RewardifycliTestCase):

    def test_login_required_decorator_working(self):
        pack_parameters = [
            {
                'name': 'Buy Me Pack',
                'cost': 100,
                'description': 'For testing',
                'slot1': [1, 0, 0, 0],
                'slot2': [1, 0, 0, 0],
                'slot3': [0, 1, 0, 0],
                'slot4': [0, 0, 1, 0],
                'slot5': [0, 0, 0, 1],
            }
        ]
        with MockConfigContext(self, packs=pack_parameters) as mock_context, StandardUserContext() as user_context:
            facade: Rewardify = Rewardify.instance()

            # Here we are invoking the buy command, without logging in a user first. The buy command is decorated with
            # the "login_required" decorator, which should make this command fail, even though the input is correct
            result = self.RUNNER.invoke(packs, ['buy', 'Buy Me Pack'])
            print(mock_context.credentials['username'])
            self.assertEqual(result.exit_code, 1)

            self.assertTrue('AUTHENTICATION FAILURE' in result.output)

    def test_buy_pack_working(self):
        pack_parameters = [
            {
                'name':         'Buy Me Pack',
                'cost':         100,
                'description':  'For testing',
                'slot1':        [1, 0, 0, 0],
                'slot2':        [1, 0, 0, 0],
                'slot3':        [0, 1, 0, 0],
                'slot4':        [0, 0, 1, 0],
                'slot5':        [0, 0, 0, 1],
            }
        ]
        with MockConfigContext(self, packs=pack_parameters) as mock_context, StandardUserContext() as user_context:
            facade: Rewardify = Rewardify.instance()
            credentials: UserCredentials = UserCredentials.instance()

            self.assertEqual(len(user_context.user.packs), 0)
            self.assertEqual(user_context.user.gold, 0)

            # After adding the necessary gold to the user, the buying operation should succeed, which means a success
            # exit code and the corresponding template being used
            facade.user_add_gold(user_context.username, 100)

            # First we need to login the user and then we double check if the new credentials are actually saved into
            # the credentials object
            self.RUNNER.invoke(login, [user_context.username, user_context.password])
            self.assertEqual(credentials['username'], user_context.username)

            result = self.RUNNER.invoke(packs, ['buy', 'Buy Me Pack'])

            self.assertEqual(result.exit_code, 0)
            self.assertTrue('PACK PURCHASE COMPLETED' in result.output)

            # If the pack purchase has worked, the user now has one pack more and no gold anymore
            user_context.update()
            self.assertEqual(len(user_context.user.packs), 1)
            self.assertEqual(user_context.user.gold, 0)

    def test_buying_without_gold_not_working(self):
        pack_parameters = [
            {
                'name': 'Buy Me Pack',
                'cost': 100,
                'description': 'For testing',
                'slot1': [1, 0, 0, 0],
                'slot2': [1, 0, 0, 0],
                'slot3': [0, 1, 0, 0],
                'slot4': [0, 0, 1, 0],
                'slot5': [0, 0, 0, 1],
            }
        ]
        with MockConfigContext(self, packs=pack_parameters) as mock_context, StandardUserContext() as user_context:
            facade: Rewardify = Rewardify.instance()

            # If the user does not have gold, the buying process should not work, instead the permission denied
            # template is to be used.
            self.assertEqual(user_context.user.gold, 0)

            self.RUNNER.invoke(login, [user_context.username, user_context.password])
            result = self.RUNNER.invoke(packs, ['buy', 'Buy Me Pack'])
            self.assertEqual(result.exit_code, 1)
            self.assertTrue('YOU CANNOT BUY THAT' in result.output)

    def test_listing_available_packs(self):
        pack_parameters = [
            {
                'name': 'Buy Me Pack',
                'cost': 100,
                'description': 'For testing',
                'slot1': [1, 0, 0, 0],
                'slot2': [1, 0, 0, 0],
                'slot3': [0, 1, 0, 0],
                'slot4': [0, 0, 1, 0],
                'slot5': [0, 0, 0, 1],
            },
            {
                'name': 'Other Pack',
                'cost': 1000,
                'description': 'For testing',
                'slot1': [1, 0, 0, 0],
                'slot2': [1, 0, 0, 0],
                'slot3': [0, 1, 0, 0],
                'slot4': [0, 0, 1, 0],
                'slot5': [0, 0, 0, 1],
            }
        ]
        with MockConfigContext(self, packs=pack_parameters) as mock_context, StandardUserContext() as user_context:
            facade: Rewardify = Rewardify.instance()

            result = self.RUNNER.invoke(packs, ['list'])
            self.assertEqual(result.exit_code, 0)
            print(result.output)
            self.assertTrue('AVAILABLE PACKS' in result.output)
            self.assertTrue('Buy Me Pack' in result.output)
            self.assertTrue('Other Pack' in result.output)

    def test_opening_a_single_pack(self):
        pack_parameters = [
            {
                'name': 'Buy Me Pack',
                'cost': 100,
                'description': 'For testing',
                'slot1': [1, 0, 0, 0],
                'slot2': [1, 0, 0, 0],
                'slot3': [0, 1, 0, 0],
                'slot4': [0, 0, 1, 0],
                'slot5': [0, 0, 0, 1],
            }
        ]
        # Since the pack is configured in a way, that it will return at least one reward of each rarity, rewards with
        # these rarities HAVE TO EXIST
        reward_parameters = [
            {
                'name': 'Common Reward',
                'description': 'for testing',
                'rarity': 'common',
                'cost': 100,
                'recycle': 100
            },
            {
                'name': 'Uncommon Reward',
                'description': 'for testing',
                'rarity': 'uncommon',
                'cost': 100,
                'recycle': 100
            },
            {
                'name': 'Rare Reward',
                'description': 'for testing',
                'rarity': 'rare',
                'cost': 100,
                'recycle': 100
            },
            {
                'name': 'Legendary Reward',
                'description': 'for testing',
                'rarity': 'legendary',
                'cost': 100,
                'recycle': 100
            }
        ]
        with MockConfigContext(self, packs=pack_parameters, rewards=reward_parameters) as mock_context, \
                StandardUserContext() as user_context:
            facade: Rewardify = Rewardify.instance()

            facade.user_add_gold(user_context.username, 100)
            facade.user_buy_pack(user_context.username, 'Buy Me Pack')

            self.RUNNER.invoke(login, [user_context.username, user_context.password])
            result = self.RUNNER.invoke(packs, ['open', 'Buy Me Pack'])
            user_context.update()
            self.assertEqual(result.exit_code, 0)

            # After the pack has been opened the user should have 5 rewards and no packs in his inventory
            self.assertEqual(len(user_context.user.packs), 0)
            self.assertEqual(len(user_context.user.rewards), 5)

            self.assertTrue('PACK OPENING' in result.output)

    def test_opening_multiple_packs_at_once(self):
        pack_parameters = [
            {
                'name': 'Buy Me Pack',
                'cost': 100,
                'description': 'For testing',
                'slot1': [1, 0, 0, 0],
                'slot2': [1, 0, 0, 0],
                'slot3': [0, 1, 0, 0],
                'slot4': [0, 0, 1, 0],
                'slot5': [0, 0, 0, 1],
            }
        ]
        # Since the pack is configured in a way, that it will return at least one reward of each rarity, rewards with
        # these rarities HAVE TO EXIST
        reward_parameters = [
            {
                'name': 'Common Reward',
                'description': 'for testing',
                'rarity': 'common',
                'cost': 100,
                'recycle': 100
            },
            {
                'name': 'Uncommon Reward',
                'description': 'for testing',
                'rarity': 'uncommon',
                'cost': 100,
                'recycle': 100
            },
            {
                'name': 'Rare Reward',
                'description': 'for testing',
                'rarity': 'rare',
                'cost': 100,
                'recycle': 100
            },
            {
                'name': 'Legendary Reward',
                'description': 'for testing',
                'rarity': 'legendary',
                'cost': 100,
                'recycle': 100
            }
        ]
        with MockConfigContext(self, packs=pack_parameters, rewards=reward_parameters) as mock_context, \
                StandardUserContext() as user_context:
            facade: Rewardify = Rewardify.instance()

            facade.user_add_gold(user_context.username, 200)
            facade.user_buy_pack(user_context.username, 'Buy Me Pack')
            facade.user_buy_pack(user_context.username, 'Buy Me Pack')

            self.RUNNER.invoke(login, [user_context.username, user_context.password])
            result = self.RUNNER.invoke(packs, ['open', '--all', 'Buy Me Pack'])
            user_context.update()
            self.assertEqual(result.exit_code, 0)

            self.assertEqual(len(user_context.user.packs), 0)
            self.assertEqual(len(user_context.user.rewards), 10)

            self.assertTrue('PACK OPENING' in result.output)


class TestInventory(RewardifycliTestCase):

    def test_empty_inventory_working(self):
        with MockConfigContext(self) as mock_context, StandardUserContext() as user_context:

            self.RUNNER.invoke(login, [user_context.username, user_context.password])
            result = self.RUNNER.invoke(inventory)

            self.assertEqual(result.exit_code, 0)
            self.assertIn('YOUR INVENTORY', result.output)

    def test_populated_inventory_working(self):
        with MockConfigContext(self) as mock_context, StandardUserContext() as user_context:

            self.RUNNER.invoke(login, [user_context.username, user_context.password])

            facade: Rewardify = Rewardify.instance()
            facade.user_add_gold(user_context.username, 2000)
            facade.user_add_dust(user_context.username, 2000)

            facade.user_buy_pack(user_context.username, 'Standard Pack')
            facade.user_buy_pack(user_context.username, 'Standard Pack')

            facade.user_buy_reward(user_context.username, 'Standard Reward')

            result = self.RUNNER.invoke(inventory)

            print(result.output)

            self.assertEqual(result.exit_code, 0)
            self.assertIn('YOUR INVENTORY', result.output)
            self.assertIn('Standard Pack', result.output)


class TestUsers(RewardifycliTestCase):

    def test_create_user(self):
        with MockConfigContext(self) as mock_context:
            username = 'Joana'
            password = 'secret'

            facade: Rewardify = Rewardify.instance()
            self.assertFalse(facade.exists_user(username))

            result = self.RUNNER.invoke(users, ['create', username, password])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('USER CREATED', result.output)

            self.assertTrue(facade.exists_user(username))


class TestRewards(RewardifycliTestCase):

    def test_buying_rewards_works(self):
        with MockConfigContext(self) as mock_context, StandardUserContext() as user_context:
            facade: Rewardify = Rewardify.instance()
            credentials: UserCredentials = UserCredentials.instance()

            self.assertEqual(len(user_context.user.rewards), 0)

            facade.user_add_dust(user_context.username, 100)

            self.RUNNER.invoke(login, [user_context.username, user_context.password])
            result = self.RUNNER.invoke(rewards, ['buy', 'Standard Reward'])
            user_context.update()

            self.assertEqual(result.exit_code, 0)
            self.assertIn('REWARD PURCHASE COMPLETED', result.output)

            self.assertEqual(user_context.user.dust, 0)
            self.assertEqual(len(user_context.user.rewards), 1)

    def test_listing_rewards(self):
        reward_parameters = [
            {
                'name': 'Common Reward',
                'description': 'for testing',
                'rarity': 'common',
                'cost': 100,
                'recycle': 100
            },
            {
                'name': 'Uncommon Reward',
                'description': 'for testing',
                'rarity': 'uncommon',
                'cost': 100,
                'recycle': 100
            },
            {
                'name': 'Rare Reward',
                'description': 'for testing',
                'rarity': 'rare',
                'cost': 100,
                'recycle': 100
            },
            {
                'name': 'Legendary Reward',
                'description': 'for testing',
                'rarity': 'legendary',
                'cost': 100,
                'recycle': 100
            }
        ]
        with MockConfigContext(self, rewards=reward_parameters) as mock_context, StandardUserContext() as user_context:
            facade: Rewardify = Rewardify.instance()

            result = self.RUNNER.invoke(rewards, ['list'])

            print(result.output)

            self.assertEqual(result.exit_code, 0)
            self.assertIn('AVAILABLE REWARDS', result.output)
            self.assertIn('Common Reward', result.output)

    def test_using_single_reward(self):
        with MockConfigContext(self) as mock_context, StandardUserContext() as user_context:
            facade: Rewardify = Rewardify.instance()

            facade.user_add_dust(user_context.username, 100)
            facade.user_buy_reward(user_context.username, 'Standard Reward')
            user_context.update()
            self.assertEqual(len(user_context.user.rewards), 1)

            self.RUNNER.invoke(login, [user_context.username, user_context.password])
            result = self.RUNNER.invoke(rewards, ['use', 'Standard Reward'])

            print(result.output)

            self.assertEqual(result.exit_code, 0)
            self.assertIn('REWARD USED', result.output)

    def test_using_multiple_rewards(self):
        reward_parameters = [
            {
                'name': 'Gold Reward',
                'description': 'for testing',
                'rarity': 'common',
                'effect': 'gold(100)',
                'cost': 100,
                'recycle': 100
            },
        ]
        with MockConfigContext(self, rewards=reward_parameters) as mock_context, StandardUserContext() as user_context:
            facade: Rewardify = Rewardify.instance()

            facade.user_add_dust(user_context.username, 200)
            facade.user_buy_reward(user_context.username, 'Gold Reward')
            facade.user_buy_reward(user_context.username, 'Gold Reward')

            self.RUNNER.invoke(login, [user_context.username, user_context.password])
            result = self.RUNNER.invoke(rewards, ['use', '--all', 'Gold Reward'])
            user_context.update()

            self.assertEqual(result.exit_code, 0)
            self.assertIn('REWARD USED', result.output)

            self.assertEqual(len(user_context.user.rewards), 0)
            self.assertEqual(user_context.user.gold, 200)

    def test_recycle_reward(self):
        reward_parameters = [
            {
                'name': 'Gold Reward',
                'description': 'for testing',
                'rarity': 'common',
                'effect': 'gold(100)',
                'cost': 100,
                'recycle': 100
            },
        ]
        with MockConfigContext(self, rewards=reward_parameters) as mock_context, StandardUserContext() as user_context:
            facade: Rewardify = Rewardify.instance()

            facade.user_add_dust(user_context.username, 100)
            facade.user_buy_reward(user_context.username, 'Gold Reward')

            self.RUNNER.invoke(login, [user_context.username, user_context.password])
            result = self.RUNNER.invoke(rewards, ['recycle', 'Gold Reward'])
            user_context.update()

            self.assertEqual(result.exit_code, 0)
            self.assertIn('REWARD RECYCLED', result.output)
            self.assertEqual(user_context.user.dust, 100)
