
import unittest

from netlookup.prefixes import NetworkSet

from ..constants import VALID_SUBNET_VALUES, INVALID_SUBNET_VALUES


class TestNetworkSets(unittest.TestCase):
    """
    Test cases for network sets
    """

    def test_create_empty_network_set(self):
        """
        Create empty network set with various arguments
        """
        network_set = NetworkSet()
        self.assertIsInstance(network_set.networks, list)

        for testcase in VALID_SUBNET_VALUES:
            network_set.add_network(testcase)
