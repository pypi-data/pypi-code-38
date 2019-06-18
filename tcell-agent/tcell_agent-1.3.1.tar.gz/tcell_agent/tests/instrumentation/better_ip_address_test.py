import unittest

from tcell_agent.instrumentation.better_ip_address import better_ip_address
from tcell_agent.tests.support.builders import ConfigurationBuilder
from tcell_agent.tests.support.context_library import ConfigContext


class BetterIpAddressTest(unittest.TestCase):
    def test_empty_env_better_ip_address(self):
        with ConfigContext(ConfigurationBuilder().build()):
            remote_address = better_ip_address({})
        self.assertEqual(remote_address, "1.1.1.1")
