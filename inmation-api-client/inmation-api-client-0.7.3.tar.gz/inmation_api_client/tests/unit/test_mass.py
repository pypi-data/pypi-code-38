import unittest

from inmation_api_client.options import Options
from .base import TestBase


class TestMass(TestBase):
    def setUp(self):
        pass

    def test_can_create_gen_folder_using_mass(self):
        res = self.client.Mass(
            [{
                'path': self.path + '/MassItem1',
                'operation': 'UPSERT',
                'class': 'GenFolder',
                'ObjectName': 'MassItem1'
            }]
        )
        self.assertEqual(res['code'], 200)
        self.assertNotIn('error', res['data']['items'][0].keys())

    def test_can_create_gen_folder_using_mass_async(self):
        res = self.run_coro(self.client.MassAsync(
            [{
                'path': self.path + '/MassItem2',
                'operation': 'UPSERT',
                'class': 'GenFolder',
                'ObjectName': 'MassItem2'
            }]
        ))
        self.assertEqual(res['code'], 200)
        self.assertNotIn('error', res['data']['items'][0].keys())

    def test_can_create_gen_folder_using_mass_with_fields(self):
        opt = Options()
        opt.fields = ['ALL']
        res = self.client.Mass(
            [{
                'path': self.path + '/MassItem3',
                'operation': 'UPSERT',
                'class': 'GenFolder',
                'ObjectName': 'MassItem3'
            }],
            opt
        )
        self.assertEqual(res['code'], 200)
        self.assertIn('c', res['data']['items'][0].keys())
        self.assertNotIn('error', res['data']['items'][0].keys())

    def test_can_create_gen_folder_using_mass_with_batch_flags(self):
        opt = Options()
        opt.batch_flags = 4  # SUPPRESS_RESULTS
        res = self.client.Mass(
            [{
                'path': self.path + '/MassItem4',
                'operation': 'UPSERT',
                'class': 'GenFolder',
                'ObjectName': 'MassItem4'
            }],
            opt
        )
        self.assertEqual(res['code'], 200)
        self.assertEqual(res['type'], 'mass')
        self.assertNotIn('data', res.keys())
