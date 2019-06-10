
import unittest

from netlookup.subnet import Network
from netaddr.core import AddrFormatError

from ..constants import VALID_SUBNET_VALUES, INVALID_SUBNET_VALUES

# How many times we may try splitting
MAX_SPLITS = 8


class TestSubnetParsing(unittest.TestCase):
    """
    Test subnet value parsing and operations
    """

    def validate_network(self, value):
        """
        Validate a network value
        """
        network = Network(value)
        return network

    def test_valid_subnet_values(self):
        """
        Test parsing of valid values for subnet object
        """
        for value in VALID_SUBNET_VALUES:
            self.validate_network(value)

    def test_invalid_subnet_values(self):
        """
        Test parsing of invalid values for subnet object
        """
        for value in INVALID_SUBNET_VALUES:
            with self.assertRaises(AddrFormatError):
                self.validate_network(value)

    def test_integer_compare_functions(self):
        """
        Test integer compare functions for extended subnet objects
        """
        for value in VALID_SUBNET_VALUES:
            network = self.validate_network(value)
            self.assertTrue(network == network.value)
            self.assertTrue(network != network.value - 1)
            self.assertTrue(network < network.last + 1)
            self.assertTrue(network <= network.last)
            self.assertTrue(network > network.value - 1)
            self.assertTrue(network >= network.value)

    def test_last_host_property(self):
        """
        Test custom last_host property
        """
        for value in VALID_SUBNET_VALUES:
            network = self.validate_network(value)
            if network.version == 4 and network.prefixlen == 31:
                self.assertEqual(network.last_host.value, network.last)
            elif network.version == 4 and network.prefixlen == 32:
                self.assertIsNone(network.last_host)
            elif network.version == 6 and network.prefixlen == 127:
                self.assertEqual(network.last_host.value, network.last)
            elif network.version == 6 and network.prefixlen == 128:
                self.assertIsNone(network.last_host)
            else:
                self.assertEqual(network.last_host.value, network.last - 1)

    def test_first_host_property(self):
        """
        Test custom last_host property
        """
        for value in VALID_SUBNET_VALUES:
            network = self.validate_network(value)
            if network.version == 4 and network.prefixlen == 32:
                self.assertIsNone(network.first_host)
            elif network.version == 4 and network.prefixlen == 31:
                self.assertEqual(network.first_host.value, network.first)
            elif network.version == 6 and network.prefixlen == 127:
                self.assertEqual(network.first_host.value, network.first)
            elif network.version == 6 and network.prefixlen == 128:
                self.assertIsNone(network.first_host)
            else:
                self.assertEqual(network.first_host.value, network.first + 1)

    def test_splitting_v4_subnets(self):
        """
        Test splitting subnet
        """
        for value in VALID_SUBNET_VALUES:
            network = self.validate_network(value)
            if network.version == 4:
                prefixlen = network.prefixlen + 1
                if prefixlen == 0:
                    prefixlen += 1
                while prefixlen < 32 and prefixlen < network.prefixlen + MAX_SPLITS:
                    testdata = list(network.subnet(prefixlen))
                    self.assertTrue(len(testdata) > 0)
                    prefixlen += 1

    def test_splitting_v6_subnets(self):
        """
        Test splitting IPv4 subnets
        """
        for value in VALID_SUBNET_VALUES:
            network = self.validate_network(value)
            if network.version == 6:
                prefixlen = network.prefixlen + 1
                if prefixlen == 0:
                    prefixlen += 1
                while prefixlen < 128 and prefixlen < network.prefixlen + MAX_SPLITS:
                    testdata = list(network.subnet(prefixlen))
                    self.assertTrue(len(testdata) > 0)
                    prefixlen += 1
