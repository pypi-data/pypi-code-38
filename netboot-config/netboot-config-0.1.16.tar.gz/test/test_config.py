from assertpy import assert_that

from netboot_config import Config


class TestConfig(object):

    def setup_method(self):
        self.uut = Config('netboot-config.yml')

    def test_netboot_host(self):
        assert_that(self.uut.netboot_host).is_equal_to("10.0.10.11")

    def test_hosts_names(self):
        hosts = self.uut.hosts
        assert_that([host.host_name for host in hosts]).contains("abc1110", "abc1111", "abc1120")

    def test_hosts_image_types(self):
        hosts = self.uut.hosts
        assert_that([host.image_type for host in hosts]).contains("type1", "type1", "type2")

    def test_hosts_image_config(self):
        hosts = self.uut.hosts
        assert_that([host.config for host in hosts]).contains((), (), (('src', 'tgt'),))

    def test_static_hosts_names(self):
        hosts = self.uut.static_hosts
        assert_that([host.host_name for host in hosts]).contains("abc1005", "abc1020", "abc1021", "abc1030", "abc1040")

    def test_static_hosts_image_types(self):
        hosts = self.uut.static_hosts
        assert_that([host.image_type for host in hosts]).contains(None, None, None, None, None)

    def test_static_hosts_image_aliases(self):
        hosts = self.uut.static_hosts
        assert_that([host.aliases for host in hosts]).contains((), (), (), ('foo',), ('bar', 'baz'))

    def test_all_hosts(self):
        assert_that(len(self.uut.all_hosts)).is_equal_to(8)

    def test_host_in_static_network(self):
        host = self.uut.get_host('10.0.10.99')
        assert_that(host.host_name).is_equal_to("abc1099")

    def test_host_in_dynamic_network(self):
        host = self.uut.get_host('10.0.11.99')
        assert_that(host.host_name).is_equal_to("abc1199")

    def test_host_outside_networks(self):
        host = self.uut.get_host('10.0.12.99')
        assert_that(host).is_none()

