# standard library
import datetime

from unittest import TestCase

# local imports
from rewardify._util_test import DBTestCase

from rewardify.adapters import PackParametersAdapter, RewardParametersAdapter

from rewardify.rarity import Rarity


class TestAdaptersRaw(TestCase):

    def test_pack_adapter(self):
        # These are the informations, that would be given to the adapter coming from the config file
        name = 'Misc Pack'
        config = {
            'description':          'this is only for testing purposes',
            'cost':                 100,
            '1':                    [1, 0, 0, 0],
            '2':                    [1, 0, 0, 0],
            '3':                    [1, 0, 0, 0],
            '4':                    [1, 0, 0, 0],
            '5':                    [1, 0, 0, 0]
        }

        adapter = PackParametersAdapter(name, config)
        parameters = adapter.parameters()

        self.assertEqual(parameters['name'], name)
        self.assertListEqual(parameters['slot1'], [1, 0, 0, 0])
        self.assertIsInstance(parameters['date_obtained'], datetime.datetime)
        self.assertEqual(parameters['gold_cost'], 100)

    def test_reward_adapter(self):
        # These are the informations, that would be given to the adapter coming from the config file
        name = 'Misc Reward'
        config = {
            'description':          'this is only for testing purposes',
            'rarity':               'common',
            'recycle':              500,
            'cost':                 1000,
        }

        adapter = RewardParametersAdapter(name, config)
        parameters = adapter.parameters()

        self.assertEqual(parameters['name'], name)
        self.assertEqual(parameters['rarity'], Rarity.COMMON)
        self.assertEqual(parameters['dust_cost'], 1000)
        self.assertIsInstance(parameters['date_obtained'], datetime.datetime)
