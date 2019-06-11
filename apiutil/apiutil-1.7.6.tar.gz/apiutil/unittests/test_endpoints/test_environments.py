# encoding: utf-8

import unittest
import apiutil
from apiutil import _metadata
from apiutil.endpoints import Environments, API, Hosts, Host

from configurationutil import configuration
configuration.DEV_FORCE_REWRITE_CONFIG = True


class TestAPIs(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_version(self):
        self.assertEqual(apiutil.__version__, _metadata.__version__, u'Version is incorrect')

    # Instantiation
    def test_instantiation(self):
        Environments()

    def test_getitem(self):
        envs = Environments()
        env = envs.production

        self.assertTrue(isinstance(env.location, str), u'Env location type incorrect')
        self.assertTrue(isinstance(env.family_a, API), u'Env API type incorrect')
        self.assertTrue(isinstance(env.family_b, API), u'Env API type incorrect')

    def test_get_environments_for_api(self):
        envs = Environments()

        self.assertEqual([u'lab', u'production'],
                         sorted(envs.get_environments_for_api(u'api_1')),
                         u'get environments for API failed')

        self.assertEqual([u'lab'],
                         envs.get_environments_for_api(u'api_3'),
                         u'get environments for API failed')

    def test_get_environments_for_api_family(self):
        envs = Environments()

        self.assertEqual([u'lab', u'production'],
                         sorted(envs.get_environments_for_api_family(u'family_a')),
                         u'get environments for API family failed')

        self.assertEqual([u'lab', u'production'],
                         sorted(envs.get_environments_for_api_family(u'family_b')),
                         u'get environments for API family failed')

    def test_get_host_list_all(self):
        envs = Environments()
        hosts = Hosts()

        actual_all_hosts = envs.get_host_list()

        self.assertEqual(3, len(actual_all_hosts), u'Envs get host list [all] length mismatch')

        for host in actual_all_hosts:
            self.assertTrue(isinstance(host, Host), u'Envs get host list [all] (type) failed')
            self.assertEqual(hosts[host.key].domain,
                             host.domain,
                             u'Envs get host list [all] (domain) failed')

    def test_get_host_list_environment(self):
        envs = Environments()
        hosts = Hosts()

        actual_env_hosts = envs.get_host_list(environment=u'production')

        self.assertEqual(2, len(actual_env_hosts), u'Envs get host list [environment] length mismatch')

        for host in actual_env_hosts:
            self.assertTrue(isinstance(host, Host), u'Envs get host list [environment] (type) failed')
            self.assertEqual(hosts[host.key].domain,
                             host.domain,
                             u'Envs get host list [environment] (domain) failed')

    def test_get_host_list_api(self):
        envs = Environments()
        hosts = Hosts()

        actual_env_hosts = envs.get_host_list(api=u'family_b')

        self.assertEqual(2, len(actual_env_hosts), u'Envs get host list [api] length mismatch')

        for host in actual_env_hosts:
            self.assertTrue(isinstance(host, Host), u'Envs get host list [api] (type) failed')
            self.assertEqual(hosts[host.key].domain,
                             host.domain,
                             u'Envs get host list [api] (domain) failed')

    def test_get_host_list_both(self):
        envs = Environments()
        hosts = Hosts()

        actual_env_hosts = envs.get_host_list(environment=u'production',
                                              api=u'family_b')

        self.assertEqual(1, len(actual_env_hosts), u'Envs get host list [both] length mismatch')

        for host in actual_env_hosts:
            self.assertTrue(isinstance(host, Host), u'Envs get host list [both] (type) failed')
            self.assertEqual(hosts[host.key].domain,
                             host.domain,
                             u'Envs get host list [both] (domain) failed')

        host_config = envs.production.family_b.host
        actual_host = actual_env_hosts[0]

        self.assertEqual(host_config.protocol, actual_host.protocol, u'Envs get host list [both] (protocol) mismatch')
        self.assertEqual(host_config.domain, actual_host.domain, u'Envs get host list [both] (domain) mismatch')
        self.assertEqual(host_config.port, actual_host.port, u'Envs get host list [both] (port) mismatch')
        self.assertEqual(host_config.secret_key, actual_host.secret_key,
                         u'Envs get host list [both] (secret_key) mismatch')
        self.assertEqual(host_config.user, actual_host.user, u'Envs get host list [both] (user) mismatch')
        self.assertEqual(host_config.password, actual_host.password, u'Envs get host list [both] (password) mismatch')

    def test_get_host_references_all(self):
        envs = Environments()

        expected_host_references = [{'environment': 'production', 'api': 'family_a'},
                                    {'environment': 'production', 'api': 'family_b'},
                                    {'environment': 'lab', 'api': 'family_a'},
                                    {'environment': 'lab', 'api': 'family_b'}]

        self.assertEqual(expected_host_references,
                         envs.get_host_references(),
                         u'Envs get host references [all] failed')

    def test_get_host_references_host(self):
        envs = Environments()

        expected_host_references = [{'environment': 'production', 'api': 'family_b'}]

        self.assertEqual(expected_host_references,
                         envs.get_host_references(host=u'p2.example.com'),
                         u'Envs get host references [all] failed')

    def test_get_environments_for_location(self):
        envs = Environments()

        self.assertEqual([u'production'],
                         envs.get_environments_for_location(u'somewhere'),
                         u'Get Envs for location failed')

        self.assertEqual([u'lab'],
                         envs.get_environments_for_location(u'nowhere'),
                         u'Get Envs for location failed')


if __name__ == u'__main__':
    unittest.main()
