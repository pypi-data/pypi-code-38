from ipaddress import IPv4Address

from assertpy import assert_that

from netboot_config.network import HostGroup, Host


class TestHost(object):

    def setup_method(self):
        self.uut = Host('foo', IPv4Address('10.11.12.13'), 'base_image')

    def test_ipv4_address(self):
        result = self.uut.ipv4_address()

        assert_that(result).is_equal_to('10.11.12.13')

    def test_hex_ipv4_address(self):
        result = self.uut.ipv4_address_hex()

        assert_that(result).is_equal_to('0A0B0C0D')

    def test_host_name(self):
       result = self.uut.host_name()

       assert_that(result).is_equal_to('foo13')


class TestNetwork(object):

    def setup_method(self):
        self.uut = HostGroup('foo', '10.11.12.0/24')

    def test_host_addresses(self):
        self.uut.add_hosts('<image_type>', 11, 4)

        hosts = self.uut.hosts()

        addresses = [host.ipv4_address() for host in hosts]

        assert_that(addresses).contains_only('10.11.12.11', '10.11.12.12', '10.11.12.13', '10.11.12.14')

    def test_host_names(self):
        self.uut.add_hosts('<image_type>', 11, 4)

        hosts = self.uut.hosts()

        host_names = [host.host_name() for host in hosts]

        assert_that(host_names).contains_only('foo11', 'foo12', 'foo13', 'foo14')
