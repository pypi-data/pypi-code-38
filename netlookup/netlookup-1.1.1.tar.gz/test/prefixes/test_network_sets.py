
import unittest

from netlookup.network import Network
from netlookup.prefixes import NetworkSet, NetworkSetError

from ..constants import VALID_SUBNET_VALUES, INVALID_SUBNET_VALUES, MAX_SPLITS


class TestNetworkSets(unittest.TestCase):
    """
    Test cases for network sets
    """

    def test_network_set_create_empty(self):
        """
        Create empty network set with various arguments
        """
        network_set = NetworkSet()
        self.assertIsInstance(network_set.networks, list)

    def test_network_set_add_valid_networks(self):
        """
        Test loading valid network prefixes to empty network set
        """
        network_set = NetworkSet()
        for network in VALID_SUBNET_VALUES:
            network_set.add_network(network)
        self.assertEqual(len(network_set.networks), len(VALID_SUBNET_VALUES))

    def test_network_set_add_invalid_networks(self):
        """
        Test loading invalid network prefixes to empty network set
        """
        network_set = NetworkSet()
        for network in INVALID_SUBNET_VALUES:
            with self.assertRaises(NetworkSetError):
                network_set.add_network(network)
        network_count = len(network_set.networks)
        self.assertEqual(network_count, 0, 'Expected empty set, has {} networks'.format(network_count))

    def test_network_set_merged_empty(self):
        """
        Teste 'merged' property for empty network set
        """
        network_set = NetworkSet()
        self.assertEqual(network_set.merged, [])

    def test_network_set_merge_valid_networks(self):
        """
        Test merging valid network ranges
        """
        network_set = NetworkSet()
        expected = 0
        for network in VALID_SUBNET_VALUES:
            # Ignore global masks
            if Network(network).prefixlen == 0:
                continue
            network_set.add_network(network)
            expected += 1
        merged = network_set.merged
        self.assertEqual(
            len(merged),
            expected,
            'Expected {} merged networks, got {}'.format(expected, merged)
        )

    def test_network_set_merge_split_ranges(self):
        """
        Test merging split IP ranges

        Splits the range to smaller units and ensures the network set still only contains
        the original split network
        """
        network_set = NetworkSet()
        network = Network('172.31.4.0/22')
        network_set.add_network(network)

        network_count = 1
        for i in range(1, MAX_SPLITS + 1):
            prefixlen = network.prefixlen + i
            for subnet in network.subnet(prefixlen):
                network_set.add_network(subnet)
                network_count += 1
                self.assertEqual(len(network_set.networks), network_count)
                self.assertTrue(
                    len(network_set.merged) == 1,
                    'Expected 1 merged network after splitting {} by prefixlen {}'.format(
                        network,
                        prefixlen
                    )
                )
