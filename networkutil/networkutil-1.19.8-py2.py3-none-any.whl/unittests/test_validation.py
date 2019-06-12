# encoding: utf-8

import unittest
from networkutil.validation import (valid_ip, valid_ipv4, valid_ipv6,
                                    valid_ip_network, valid_ipv4_network, valid_ipv6_network,
                                    IPv4Address, IPv6Address, IPv4Network, IPv6Network)


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self.valid_addresses = {
            u'ipv4': [u'0.0.0.0',
                      u'0.0.0.1',
                      u'0.0.1.0',
                      u'0.1.0.0',
                      u'1.0.0.0',
                      u'1.1.1.1',
                      u'0.0.0.255',
                      u'0.0.255.0',
                      u'0.255.0.0',
                      u'255.0.0.0',
                      u'255.255.255.255'],
            u'ipv6': [u'::',
                      u'::1',
                      u'1::',
                      u'1:2:3:4::',
                      u'1:2:3:4:5:6:7:8',
                      u'a:b:c:d:e:f:1:2',
                      u'abcd:ef12:34fe:dcba:1234:5678:ABCD:EF90']
        }

        self.invalid_addresses = {
            u'ipv4': [u'',
                      u'0.0.0.',
                      u'.0.0.1',
                      u'0..1.0',
                      u'0.1..0',
                      u'1.0.0.x',
                      u'0.0.0.256',
                      u'0.0.300.0',
                      u'0.400.0.0',
                      u'FF.0.0.0',
                      u''],
            u'ipv6': [u'',
                      u'abcd:ef12:34fe:dcba:1234:5678:ABCD:ABCDE',
                      u'abcd:ef12:34fe:dcba:1234:5678:ABCD:EFGH',
                      u'abcd:ef12:34fe:dcba:1234:5678:ABCD.EF12',
                      u'abcd:ef12:34fe:dcba:1234:5678:ABCD']
        }

        self.valid_networks = {
            u'ipv4': [  # TODO: Complete this list
                u'0.0.0.0',
                u'192.168.0.0',
                u'192.168.0.0/24',
                u'192.168.0.0/16',
                u'192.168.0.0/255.255.255.0',
                u'192.168.0.0/255.255.0.0'
            ],
            u'ipv6': [  # TODO: Complete this list
            ]
        }

        self.invalid_networks_strict = {
            u'ipv4': [  # TODO: Complete this list
                u''
            ],
            u'ipv6': [  # TODO: Complete this list
                u''
            ]
        }

    def tearDown(self):
        pass

    # Addresses
    def test_valid_ipv4(self):
        for ip in self.valid_addresses.get(u'ipv4'):
            self.assertTrue(valid_ipv4(ip),
                            u'IP {ip} is not registering as valid IPv4'.format(ip=ip))
            self.assertTrue(valid_ip(ip),
                            u'IP {ip} is not registering as valid IPv4'.format(ip=ip))
            self.assertTrue(valid_ip(ip,
                                     method=IPv4Address),
                            u'IP {ip} is not registering as valid IPv4'.format(ip=ip))

    def test_valid_ipv6(self):
        for ip in self.valid_addresses.get(u'ipv6'):
            self.assertTrue(valid_ipv6(ip),
                            u'IP {ip} is not registering as valid IPv6'.format(ip=ip))
            self.assertTrue(valid_ip(ip),
                            u'IP {ip} is not registering as valid IPv6'.format(ip=ip))
            self.assertTrue(valid_ip(ip,
                                     method=IPv6Address),
                            u'IP {ip} is not registering as valid IPv6'.format(ip=ip))

    def test_invalid_ipv4(self):
        for ip in self.invalid_addresses.get(u'ipv4'):
            self.assertFalse(valid_ipv4(ip),
                             u'IP {ip} is not registering as invalid IPv4'.format(ip=ip))
            self.assertFalse(valid_ip(ip),
                             u'IP {ip} is not registering as invalid IPv4'.format(ip=ip))

            self.assertFalse(valid_ip(ip,
                                      method=IPv4Address),
                             u'IP {ip} is not registering as valid IPv4'.format(ip=ip))

    def test_invalid_ipv6(self):
        for ip in self.invalid_addresses.get(u'ipv6'):
            self.assertFalse(valid_ipv6(ip),
                             u'IP {ip} is not registering as invalid IPv6'.format(ip=ip))
            self.assertFalse(valid_ip(ip),
                             u'IP {ip} is not registering as invalid IPv6'.format(ip=ip))
            self.assertFalse(valid_ip(ip,
                                      method=IPv6Address),
                             u'IP {ip} is not registering as valid IPv6'.format(ip=ip))

    # Networks
    def test_valid_ipv4_network(self):
        for ip in self.valid_networks.get(u'ipv4'):
            self.assertTrue(valid_ipv4_network(ip),
                            u'Network {ip} is not registering as a valid IPv4 Network'.format(ip=ip))
            self.assertTrue(valid_ip_network(ip),
                            u'Network {ip} is not registering as a valid IPv4 Network'.format(ip=ip))
            self.assertTrue(valid_ip_network(ip,
                                             method=IPv4Network),
                            u'Network {ip} is not registering as a valid IPv4 Network'.format(ip=ip))

    def test_valid_ipv6_network(self):
        for ip in self.valid_networks.get(u'ipv6'):
            self.assertTrue(valid_ipv6_network(ip),
                            u'Network {ip} is not registering as a valid IPv6 Network'.format(ip=ip))
            self.assertTrue(valid_ip_network(ip),
                            u'Network {ip} is not registering as a valid IPv6 Network'.format(ip=ip))
            self.assertTrue(valid_ip_network(ip,
                                             method=IPv6Network),
                            u'Network {ip} is not registering as a valid IPv6 Network'.format(ip=ip))

    def test_invalid_ipv4_network(self):
        for ip in self.invalid_networks_strict.get(u'ipv4'):
            self.assertFalse(valid_ipv4_network(ip),
                             u'Network {ip} is not registering as an invalid IPv4 Network'.format(ip=ip))
            self.assertFalse(valid_ip_network(ip),
                             u'Network {ip} is not registering as an invalid IPv4 Network'.format(ip=ip))
            self.assertFalse(valid_ip_network(ip,
                                              method=IPv4Network),
                             u'Network {ip} is not registering as an invalid IPv4 Network'.format(ip=ip))

    def test_invalid_ipv6_network(self):
        for ip in self.invalid_networks_strict.get(u'ipv6'):
            self.assertFalse(valid_ipv6_network(ip),
                             u'Network {ip} is not registering as an invalid IPv6 Network'.format(ip=ip))
            self.assertFalse(valid_ip_network(ip),
                             u'Network {ip} is not registering as an invalid IPv6 Network'.format(ip=ip))
            self.assertFalse(valid_ip_network(ip,
                                              method=IPv6Network),
                             u'Network {ip} is not registering as an invalid IPv6 Network'.format(ip=ip))


if __name__ == u'__main__':
    unittest.main()
