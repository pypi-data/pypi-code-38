from __future__ import absolute_import

import unittest

import json

from rook import configuration


class TestConfigurationScheme(unittest.TestCase):

    def test_initialized_attribute(self):
        class TestScheme(configuration.ConfigurationScheme):
            A = 1

        TestScheme.A = 2

        self.assertEqual(2, TestScheme.A)


class TestConfigManager(unittest.TestCase):

    def test_load_dictionary(self):
        class Container(object):
            class TestScheme(configuration.ConfigurationScheme):
                A = 1
                B = 2

        c = configuration.ConfigManager(Container)

        c.load_dictionary({'TestScheme' : {'A' : 4, 'B': 5}})

        self.assertEqual(4, Container.TestScheme.A)
        self.assertEqual(5, Container.TestScheme.B)

    def test_load_json_file(self):
        class Container(object):
            class TestScheme(configuration.ConfigurationScheme):
                A = 1
                B = 2

        with open('test.json', 'w') as f:
            json.dump({'TestScheme' : {'A' : 4, 'B': 5}}, f)

        c = configuration.ConfigManager(Container)
        c.load_json_file('test.json')

        self.assertEqual(4, Container.TestScheme.A)
        self.assertEqual(5, Container.TestScheme.B)

    def test_load_class(self):
        class Container(object):
            class TestScheme(configuration.ConfigurationScheme):
                class TestScheme(configuration.ConfigurationScheme):
                    A = 1
                    B = 2

        class TestScheme(configuration.ConfigurationValues):
            class TestScheme(configuration.ConfigurationValues):
                A = 4
                B = 5

        c = configuration.ConfigManager(Container)
        c.load_config_class(TestScheme)

        self.assertEqual(4, Container.TestScheme.TestScheme.A)
        self.assertEqual(5, Container.TestScheme.TestScheme.B)

    def test_load_module(self):
        class Container(object):
            class TestScheme(configuration.ConfigurationScheme):
                A = 1
                B = 2

        class ValuesContainer(object):
            class TestScheme(configuration.ConfigurationValues):
                A = 4
                B = 5

        c = configuration.ConfigManager(Container)
        c.load_module(ValuesContainer)

        self.assertEqual(4, Container.TestScheme.A)
        self.assertEqual(5, Container.TestScheme.B)

    def test_dump_json_file(self):
        class Container(object):
            class TestScheme(configuration.ConfigurationScheme):
                A = 1
                B = 2

        Container.TestScheme.A = 4
        Container.TestScheme.B = 5

        c = configuration.ConfigManager(Container)
        c.dump_json_file(['TestScheme'], 'test.json')

        with open('test.json', "r") as f:
            contents = json.load(f)

        self.assertEqual({'TestScheme': {'A': 4, 'B': 5}}, contents)

    def test_dump_json_file_all(self):
        class Container(object):
            class Config1(configuration.ConfigurationScheme):
                A = 1
            class Config2(configuration.ConfigurationScheme):
                B = 2

        c = configuration.ConfigManager(Container)
        c.dump_json_file_all('test_all.json')

        with open('test_all.json', "r") as f:
            contents = json.load(f)

        self.assertEqual({'Config1': {'A': 1}, 'Config2': {'B': 2}}, contents)

    def test_dump_and_load_json_file(self):
        class Container1(object):
            class TestScheme(configuration.ConfigurationScheme):
                A = 1
                B = 2

        class Container2(object):
            class TestScheme(configuration.ConfigurationScheme):
                A = 1
                B = 2

        Container1.TestScheme.A = 4
        Container1.TestScheme.B = 5

        c1 = configuration.ConfigManager(Container1)
        c1.dump_json_file(['TestScheme'], 'test.json')

        c2 = configuration.ConfigManager(Container2)
        c2.load_json_file('test.json')

        self.assertEqual(4, Container1.TestScheme.A)
        self.assertEqual(5, Container2.TestScheme.B)
