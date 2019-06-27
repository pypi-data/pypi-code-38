import os
import socket
from unittest import skipIf

from burlap.tests.functional_tests.base import TestCase

def is_valid_ipv4_address(address):
    try:
        _ = socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            _ = socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:    # not a valid address
        return False
    return True


def is_valid_ipv6_address(address):
    try:
        _ = socket.inet_pton(socket.AF_INET6, address)
    except socket.error:    # not a valid address
        return False
    return True


def is_valid_address(address):
    return is_valid_ipv4_address(address) or is_valid_ipv6_address()


class NetworkTests(TestCase):

    @skipIf("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", "Skipping this test on Travis CI.") #TODO:fix on Travis?
    def test_interfaces_ipv4_addresses(self):

        from burlap.network import interfaces
        from burlap.network import address

        for interface in interfaces():
            ipv4_address = address(interface)
            assert is_valid_ipv4_address(ipv4_address)

    def test_loopback_interface_exists(self):
        from burlap.network import interfaces
        assert 'lo' in interfaces()

    def test_loopback_interface_address(self):
        from burlap.network import address
        assert address('lo') == '127.0.0.1'

    @skipIf("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", "Skipping this test on Travis CI.") #TODO:fix on Travis?
    def test_name_servers(self):
        from burlap.network import nameservers
        for address in nameservers():
            assert is_valid_address(address)
