import os
import unittest

from pysp.sbasic import SStrExpand, SFile
from pysp.sconf import SConfig
from pysp.serror import SDebug


class StrExpandTest(SDebug, SFile, unittest.TestCase):

    def _set_environ(self, kv):
        if kv:
            idx = kv.index('=')
            if idx > 0:
                os.environ[kv[:idx]] = kv[idx+1:]

    def test_environ_vars(self):
        testcase = (
            (True,  'ABC', 'ABC',  ''),
            (True,  'ABC', '$KEY', 'KEY=ABC'),
            (True,  'ABC.Value', '$KEY.Value', 'KEY=ABC'),
            (True,  'MyABC.Value', 'My$KEY.Value', 'KEY=ABC'),
            (True,  'ABC', '${KEY}', 'KEY=ABC'),
            (True,  'ABC.Value', '${KEY}.Value', 'KEY=ABC'),
            (True,  'MyABC.Value', 'My${KEY}.Value', 'KEY=ABC'),
            (True,  'My$NoKEY.Value', 'My$NoKEY.Value', ''),
            (True,  'My${NoKEY}.Value', 'My${NoKEY}.Value', ''),
            (True,  'MyABC$Value', 'My$KEY$Value', 'KEY=ABC'),
            (True,  'MyABC$Value', 'My$KEY$Value', 'KEY=ABC'),
            (False, 'MyABC_Value', 'My$KEY_Value', 'KEY=ABC'),
            (True,  'MyABC_Value', 'My${KEY}_Value', 'KEY=ABC'),
            (True,  'MyABC123', 'My${KEY}$Value', 'Value=123'),
        )
        for sch in '!@#%^&*()-=+{}[]|,./;:\'"`~<>?':
            testcase += (
                (True,  'MyABC{sch}value'.format(sch=sch),
                        'My${KEY}{sch}value'.format(KEY='KEY', sch=sch), ''),
                (True,  'MyABC{sch}value'.format(sch=sch),
                        'My$KEY{sch}value'.format(sch=sch), ''),
            )

        for case in testcase:
            rv, expected, string, keyvalue = case
            if keyvalue:
                self._set_environ(keyvalue)
            # print('@@', SStrExpand.environ_vars(string))
            assert rv == (expected == SStrExpand.environ_vars(string))

    def test_config_vars(self):
        yml_string = '''
vehicle:
    sedan:
        fuel: [disel, gasoline]
        wheels: 4
    suv:
        fuel: [disel, gasoline]
        wheels: 4
'''
        vehicle_file = '/tmp/test/vehicle.yml'
        self.to_file(vehicle_file, yml_string)
        cfg = SConfig(vehicle_file)
        # self.DEBUG = True

        testcase = (
            (True,  cfg,
                    'Sedan has 4 tires.',
                    'Sedan has @vehicle.sedan.wheels tires.', ''),
            (True,  cfg,
                    'Engine is two types - disel,gasoline.',
                    'Engine is two types - @{vehicle.suv.fuel}.', ''),
            (True,  cfg,
                    'Engine is two types - @vehicle.suv.fuel.',
                    'Engine is two types - @vehicle.suv.fuel.', ''),
            (True,  None,
                    'Engine is two types - @{vehicle.suv.fuel}.',
                    'Engine is two types - @{vehicle.suv.fuel}.', ''),
        )

        for case in testcase:
            rv, config, expected, string, keyvalue = case
            if keyvalue:
                self._set_environ(keyvalue)

            assert rv == (expected == SStrExpand.config_vars(config, string))

    def test_convert(self):
        yml_string = '''
vehicle:
    sedan:
        fuel: [disel, gasoline]
        wheels: 4
    suv:
        fuel: [disel, gasoline]
        wheels: 4
link: $ENV_LINK
link2: "@link"
'''
        vehicle_file = '/tmp/test/vehicle.yml'
        self.to_file(vehicle_file, yml_string)
        cfg = SConfig(vehicle_file)
        # self.DEBUG = True

        testcase = (
            (True,  cfg,
                    'Sedan has 4 tires.',
                    'Sedan has @vehicle.sedan.wheels tires.', ''),
            (True,  cfg,
                    'Engine is two types - disel,gasoline.',
                    'Engine is two types - @{vehicle.suv.fuel}.', ''),
            (True,  cfg,
                    'Engine is two types - @vehicle.suv.fuel.',
                    'Engine is two types - @vehicle.suv.fuel.', ''),
            (True,  None,
                    'Engine is two types - @{vehicle.suv.fuel}.',
                    'Engine is two types - @{vehicle.suv.fuel}.', ''),
            (True,  cfg,
                    'All vehicle has not 4 tires.',
                    'All vehicle has not $VEHICLE_TIRES tires.',
                    'VEHICLE_TIRES=@{vehicle.sedan.wheels}'),
            (True,  cfg,
                    '$ENV_LINK',
                    '$ENV_LINK',
                    'ENV_LINK=@link'),
            (True,  None,
                    '@link',
                    '$ENV_LINK',
                    'ENV_LINK=@link'),
        )

        for case in testcase:
            rv, config, expected, string, keyvalue = case
            if keyvalue:
                self._set_environ(keyvalue)
            result = SStrExpand.convert(string, config=config)
            assert rv == (expected == result)

        self._set_environ('ENV_LINK=@link2')
        try:
            SStrExpand.convert('@link', config=cfg)
            assert False
        except SStrExpand.Error:
            pass
