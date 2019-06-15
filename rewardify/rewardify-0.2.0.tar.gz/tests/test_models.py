# Standard library
import datetime

# Third party imports
from peewee import IntegrityError

# local imports
from rewardify._util_test import DBTestCase
from rewardify.models import User, Pack, Reward


class TestModels(DBTestCase):

    # SAMPLE USER MODEL VALUES
    # ------------------------

    SAMPLE_USER_NAME = 'Jonas'
    SAMPLE_USER_PASSWORD = 'super secret'

    # SAMPLE PACK MODEL VALUES
    # ------------------------

    SAMPLE_PACK_NAME = 'Sample Pack'
    SAMPLE_PACK_SLUG = 'sample_pack'
    SAMPLE_PACK_DESCRIPTION = 'The most basic of basic packs'
    SAMPLE_PACK_GOLD = 1000
    SAMPLE_PACK_PROBABILITY = [0.25, 0.25, 0.25, 0.25]
    SAMPLE_PACK_DATE = datetime.datetime.now()

    # SAMPLE REWARD MODEL VALUES
    # --------------------------

    SAMPLE_REWARD_NAME = 'Sample Reward'
    SAMPLE_REWARD_SLUG = 'sample_reward'
    SAMPLE_REWARD_DESCRIPTION = 'The most simple reward: you get nothing'
    SAMPLE_REWARD_DUST = 1000
    SAMPLE_REWARD_DUST_RECYCLE = 500
    SAMPLE_REWARD_RARITY = 'common'
    SAMPLE_REWARD_DATE = datetime.datetime.now()
    # 15.06.2019
    # In the new version, the Reward class has an additional field "effect"
    SAMPLE_REWARD_EFFECT = ''

    # GENERAL TEST CASES
    # ------------------

    def test_database_working(self):
        # Creating the user and saving it into the database
        user = User(
            name=self.SAMPLE_USER_NAME,
            password=self.SAMPLE_USER_PASSWORD,
            gold=0,
            dust=0
        )
        user.save()

        # Attempting to load it
        user = User.get(User.name == self.SAMPLE_USER_NAME)
        self.assertTrue(user.password.check(self.SAMPLE_USER_PASSWORD))

    def test_database_modifications_do_not_transcend_individual_tests(self):
        users = User.select().where(User.name == self.SAMPLE_USER_NAME)
        # If other test cases indeed do not influence the
        self.assertEqual(len(users), 0)

    # USER MODEL SPECIFIC TEST CASES
    # ------------------------------

    def test_user_adding_gold_and_dust_works(self):
        # Setting up the database
        self.setup_sample_user()

        # Loading the user, adding to its gold and dust, saving it again and loading it again to check if the
        # changes have stayed
        user = User.get(User.name == self.SAMPLE_USER_NAME)
        self.assertEqual(user.gold, 0)
        self.assertEqual(user.dust, 0)

        user.gold += 100
        user.dust += 100
        user.save()

        user = User.get(User.name == self.SAMPLE_USER_NAME)
        self.assertEqual(user.gold, 100)
        self.assertEqual(user.dust, 100)

    def test_user_join_reward_and_pack_columns(self):
        # Setting all up
        self.setup_sample_user()
        self.setup_sample_pack()
        self.setup_sample_reward()

        # Attempting to get a user object with all the correct back refs to the pack and reward objects
        users = User.select(User).where(User.name == self.SAMPLE_USER_NAME)
        user = users[0]

        self.assertEqual(len(user.rewards), 1)
        self.assertEqual(user.rewards[0].name, self.SAMPLE_REWARD_NAME)

        self.assertEqual(len(user.packs), 1)
        self.assertEqual(user.packs[0].name, self.SAMPLE_PACK_NAME)

    # PACK MODEL SPECIFIC TEST CASES
    # ------------------------------

    def test_pack_creation_works(self):
        # Setting up the database
        self.setup_sample_user()

        user = User.get(User.name == self.SAMPLE_USER_NAME)
        pack = Pack(
            name='Simple Pack',
            slug='simple_pack',
            description='The most basic of rewards',
            gold_cost=1000,
            date_obtained=datetime.datetime.now(),
            slot1=self.SAMPLE_PACK_PROBABILITY,
            slot2=self.SAMPLE_PACK_PROBABILITY,
            slot3=self.SAMPLE_PACK_PROBABILITY,
            slot4=self.SAMPLE_PACK_PROBABILITY,
            slot5=self.SAMPLE_PACK_PROBABILITY,
            user=user
        )
        pack.save()

        # Loading the pack to see it it worked
        pack = Pack.get(Pack.slug == 'simple_pack')
        self.assertEqual(pack.name, 'Simple Pack')

    def test_pack_joining_user_column_works(self):
        self.setup_sample_user()
        self.setup_sample_pack()

        packs = Pack.select(Pack, User).join(User).where(Pack.name == self.SAMPLE_PACK_NAME)
        self.assertGreaterEqual(len(packs), 1)
        pack = packs[0]

        self.assertEqual(pack.user.name, self.SAMPLE_USER_NAME)

    def test_pack_multiple_unique_slugs_fails(self):
        self.setup_sample_user()
        self.setup_sample_pack()

        # Now we are trying to create yet another Pack entry, but with the same slug. As the slug is a unique index
        # this should fail in some way
        user = self.get_sample_user()
        new_pack = Pack(
            name='Different Pack',
            slug=self.SAMPLE_PACK_SLUG,
            description='Different description',
            gold_cost=100,
            slot1=self.SAMPLE_PACK_PROBABILITY,
            slot2=self.SAMPLE_PACK_PROBABILITY,
            slot3=self.SAMPLE_PACK_PROBABILITY,
            slot4=self.SAMPLE_PACK_PROBABILITY,
            slot5=self.SAMPLE_PACK_PROBABILITY,
            user=user,
        )
        self.assertRaises(
            IntegrityError,
            new_pack.save
        )

    # REWARD MODEL SPECIFIC TEST CASES
    # --------------------------------

    def test_reward_creation_works(self):
        self.setup_sample_user()
        # Saving the object into the database
        user = self.get_sample_user()
        name_string = 'Simple Reward'
        slug_string = 'simple slug'
        reward = Reward(
            name=name_string,
            slug=slug_string,
            description='Simple Reward, get nothing',
            dust_cost=100,
            dust_recycle=1,
            date_obtained=datetime.datetime.now(),
            effect='',
            rarity='legendary',
            user=user
        )
        reward.save()

        # Loading the model
        reward = Reward.get(Reward.slug == slug_string)
        self.assertEqual(reward.name, name_string)

    # HELPER METHODS FOR SETTING UP
    # -----------------------------

    def setup_sample_user(self):
        # Creating the user and saving it into the database
        user = User(
            name=self.SAMPLE_USER_NAME,
            password=self.SAMPLE_USER_PASSWORD,
            gold=0,
            dust=0
        )
        user.save()

    def get_sample_user(self):
        return User.get(User.name == self.SAMPLE_USER_NAME)

    def setup_sample_pack(self):
        # Loading the sample user to be the owner of this pack
        user = User.get(User.name == self.SAMPLE_USER_NAME)
        pack = Pack(
            name=self.SAMPLE_PACK_NAME,
            slug=self.SAMPLE_PACK_SLUG,
            description=self.SAMPLE_PACK_DESCRIPTION,
            gold_cost=self.SAMPLE_PACK_GOLD,
            date_obtained=self.SAMPLE_PACK_DATE,
            slot1=self.SAMPLE_PACK_PROBABILITY,
            slot2=self.SAMPLE_PACK_PROBABILITY,
            slot3=self.SAMPLE_PACK_PROBABILITY,
            slot4=self.SAMPLE_PACK_PROBABILITY,
            slot5=self.SAMPLE_PACK_PROBABILITY,
            user=user
        )
        pack.save()

    def setup_sample_reward(self):
        user = self.get_sample_user()
        reward = Reward(
            name=self.SAMPLE_REWARD_NAME,
            slug=self.SAMPLE_REWARD_SLUG,
            description=self.SAMPLE_REWARD_DESCRIPTION,
            dust_cost=self.SAMPLE_REWARD_DUST,
            dust_recycle=self.SAMPLE_REWARD_DUST_RECYCLE,
            date_obtained=self.SAMPLE_REWARD_DATE,
            rarity=self.SAMPLE_REWARD_RARITY,
            effect=self.SAMPLE_REWARD_EFFECT,
            user=user,
        )
        reward.save()


class TestUser(DBTestCase):

    SAMPLE_USER_PARAMETERS = {
        'name':         'Jonas',
        'password':     'secret',
        'dust':         0,
        'gold':         0
    }

    SAMPLE_PACK_PARAMETERS = {
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

    # This dict has key names in such a way, that it can be directly unpacked into the constructor of the Reward class
    # to create new instance
    # 15.06.2019
    # Added the effect parameter (Which will contain a string, that eventually contains a directive of what effect the
    # rewards has for the program)
    SAMPLE_REWARD_PARAMETERS = {
        'name':             'Sample Reward',
        'slug':             'sample_reward',
        'description':      'testing',
        'effect':           '',
        'rarity':           1,
        'date_obtained':    datetime.datetime.now(),
        'dust_cost':        100,
        'dust_recycle':     100,
    }

    # ACTUAL TESTS
    # ------------

    def test_buying_a_pack(self):
        self.create_sample_user()
        user = self.get_sample_user()

        # Obviously the user should not have packs in the beginning
        self.assertEqual(len(user.packs), 0)
        user.gold += 1000
        user.buy_pack(self.SAMPLE_PACK_PARAMETERS)
        user.save()

        self.assertEqual(user.gold, 1000 - self.SAMPLE_PACK_PARAMETERS['gold_cost'])
        self.assertTrue(len(user.packs) == 1)

    def test_buying_a_pack_without_gold(self):
        self.create_sample_user()
        user = self.get_sample_user()

        self.assertRaises(
            PermissionError,
            user.buy_pack,
            self.SAMPLE_PACK_PARAMETERS
        )

    def test_buying_a_reward(self):
        self.create_sample_user()
        user = self.get_sample_user()

        self.assertEqual(len(user.rewards), 0)
        user.dust += 1000
        user.buy_reward(self.SAMPLE_REWARD_PARAMETERS)
        user.save()
        self.assertEqual(user.dust, 1000 - self.SAMPLE_REWARD_PARAMETERS['dust_cost'])

        self.assertEqual(len(user.rewards), 1)

    def test_buying_a_reward_without_gold(self):
        self.create_sample_user()
        user = self.get_sample_user()

        self.assertRaises(
            PermissionError,
            user.buy_reward,
            self.SAMPLE_REWARD_PARAMETERS
        )

    def test_recycling_a_reward(self):
        self.create_sample_user()
        user = self.get_sample_user()

        user.add_reward(self.SAMPLE_REWARD_PARAMETERS)
        user.save()

        self.assertEqual(len(user.rewards), 1)
        user.recycle_reward(self.SAMPLE_REWARD_PARAMETERS['name'])
        self.assertEqual(len(user.rewards), 0)
        self.assertEqual(user.dust, self.SAMPLE_REWARD_PARAMETERS['dust_recycle'])

    def test_packs_by_name_dict(self):
        self.create_sample_user()
        user = self.get_sample_user()

        pack_parameters = [
            {
                'name': 'Sample Pack',
                'slug': 'sample_pack',
                'description': 'testing',
                'gold_cost': 100,
                'date_obtained': datetime.datetime.now(),
                'slot1': [1, 0, 0, 0],
                'slot2': [1, 0, 0, 0],
                'slot3': [1, 0, 0, 0],
                'slot4': [1, 0, 0, 0],
                'slot5': [1, 0, 0, 0],
            },
            {
                'name': 'Sample Pack',
                'slug': 'sample_pack',
                'description': 'testing',
                'gold_cost': 100,
                'date_obtained': datetime.datetime.now(),
                'slot1': [1, 0, 0, 0],
                'slot2': [1, 0, 0, 0],
                'slot3': [1, 0, 0, 0],
                'slot4': [1, 0, 0, 0],
                'slot5': [1, 0, 0, 0],
            },
            {
                'name': 'Crumble Pack',
                'slug': 'crumble_pack',
                'description': 'testing',
                'gold_cost': 100,
                'date_obtained': datetime.datetime.now(),
                'slot1': [1, 0, 0, 0],
                'slot2': [1, 0, 0, 0],
                'slot3': [1, 0, 0, 0],
                'slot4': [1, 0, 0, 0],
                'slot5': [1, 0, 0, 0],
            }
        ]
        for pack_parameter in pack_parameters:
            user.add_pack(pack_parameter)
        user.save()

        # So the packs that have been added to the user just now where two "Sample Pack" and one "Crumble Pack".
        # This means, that the pack name mapping dict should contain these two names as keys with the one having a
        # length 2 list as value and the other a length 1 list
        packs_dict = user.get_packs_by_name()
        self.assertEqual(len(packs_dict), 2)
        self.assertListEqual(list(packs_dict.keys()), ['Sample Pack', 'Crumble Pack'])
        self.assertEqual(len(packs_dict['Sample Pack']), 2)
        self.assertEqual(len(packs_dict['Crumble Pack']), 1)

    def test_rewards_by_name_dict(self):
        self.create_sample_user()
        user = self.get_sample_user()

        reward_parameters = [
            {
                'name': 'Sample Reward',
                'slug': 'sample_reward',
                'description': 'testing',
                'effect': '',
                'rarity': 1,
                'date_obtained': datetime.datetime.now(),
                'dust_cost': 100,
                'dust_recycle': 100,
            },
            {
                'name': 'Sample Reward',
                'slug': 'sample_reward',
                'description': 'testing',
                'rarity': 1,
                'effect': '',
                'date_obtained': datetime.datetime.now(),
                'dust_cost': 100,
                'dust_recycle': 100,
            },
            {
                'name': 'Crumble Reward',
                'slug': 'crumble_reward',
                'description': 'testing',
                'rarity': 1,
                'effect': '',
                'date_obtained': datetime.datetime.now(),
                'dust_cost': 100,
                'dust_recycle': 100,
            }
        ]
        for reward_parameter in reward_parameters:
            user.add_reward(reward_parameter)

        # This method is supposed to return a dict, whose keys are the names of the rewards types and the values are
        # lists with all Reward objects of that type from the users inventory
        rewards_dict = user.get_rewards_by_name()
        # Just now 2 "Sample Reward" and 1 "Crumble Reward" have been added, which means, that the name reward map has
        # to contain these two as the keys and the one value has to be a length 2 list, the other a length 1 list
        self.assertEqual(len(rewards_dict), 2)
        self.assertListEqual(list(rewards_dict.keys()), ['Sample Reward', 'Crumble Reward'])
        self.assertEqual(len(rewards_dict['Sample Reward']), 2)
        self.assertEqual(len(rewards_dict['Crumble Reward']), 1)

    # HELPER METHODS
    # --------------

    def create_sample_user(self):
        user = User(**self.SAMPLE_USER_PARAMETERS)
        user.save()

    def get_sample_user(self) -> User:
        user = User.get(User.name == self.SAMPLE_USER_PARAMETERS['name'])
        return user


class TestReward(DBTestCase):

    # THE STANDARD MODELS
    # -------------------

    STANDARD_USER_PARAMETERS = {
        'name':         'Jonas',
        'password':     'secret',
        'dust':         0,
        'gold':         0,
    }

    STANDARD_REWARD_PARAMETERS = {
        'name':             'Standard reward',
        'slug':             'standard_reward',
        'description':      'testing',
        'dust_cost':        100,
        'dust_recycle':     50,
        'date_obtained':    datetime.datetime.now(),
        'rarity':           'common',
        'effect':           ''
    }

    # ACTUAL TESTS
    # ------------

    def test_recycle_reward(self):
        self.create_standard_user()
        user = self.get_standard_user()
        user.add_reward(self.STANDARD_REWARD_PARAMETERS)

        # At this point the standard user should have one reward an not dust
        self.assertEqual(len(user.rewards), 1)
        self.assertEqual(user.gold, 0)

        # Now we recycle the reward and for the standard reward this should be 50 dust
        reward = user.rewards[0]
        self.assertEqual(reward.recycle(), 50)

    def test_evaluate_gold_effect(self):
        self.create_standard_user()
        user = self.get_standard_user()

        self.assertEqual(user.gold, 0)
        # Now we add a user with a gold effect to the user and after we have evaluated it the user should have gone
        # from 0 to 100 gold
        reward_parameters = self.STANDARD_REWARD_PARAMETERS
        reward_parameters.update({'effect': 'gold(100)'})
        user.add_reward(reward_parameters)

        reward = user.rewards[0]
        reward.evaluate_effect()

        user = self.get_standard_user()
        self.assertEqual(user.gold, 100)

    def test_evaluate_gold_and_dust_effect_in_one_string(self):
        self.create_standard_user()
        user = self.get_standard_user()

        self.assertEqual(user.gold, 0)
        # Now we add a user with a gold and dust effect to the user and after we have evaluated it the user should have
        # gone from 0 to 100 gold and from 0 to 200 dust
        reward_parameters = self.STANDARD_REWARD_PARAMETERS
        reward_parameters.update({'effect': 'gold(100) dust(200)'})
        user.add_reward(reward_parameters)

        reward = user.rewards[0]
        reward.evaluate_effect()

        user = self.get_standard_user()
        self.assertEqual(user.gold, 100)
        self.assertEqual(user.dust, 200)

    # HELPER METHODS
    # --------------

    def create_standard_user(self):
        user = User(**self.STANDARD_USER_PARAMETERS)
        user.save()

    def get_standard_user(self):
        return User.get(User.name == self.STANDARD_USER_PARAMETERS['name'])
